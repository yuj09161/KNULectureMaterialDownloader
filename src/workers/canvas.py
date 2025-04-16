from base64 import b64decode
from collections.abc import Iterable
from concurrent.futures import Executor, ThreadPoolExecutor, Future
from functools import reduce
from html import unescape as html_unescape
from http.cookiejar import Cookie
from itertools import repeat, chain
from operator import add
from typing import NamedTuple
import xml.etree.ElementTree as et
import json
import os
import re
import urllib.parse
import warnings


from bs4 import BeautifulSoup, Tag, XMLParsedAsHTMLWarning
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from Crypto.Hash import SHA256
import requests

from pyside_commons import ThreadRunner
from . import MaterialTypes, LectureMaterial


CANVAS_SESSION = '_normandy_session'
LEARNINGX_SESSION = 'xn_api_token'

CANVAS_URL = 'https://canvas.knu.ac.kr'
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'


def _join_url_token(
    url: str, access_token: str, options: Iterable = None
) -> str:
    if options:
        return url + '?access_token=' + access_token + '&' + '&'.join(options)
    return url + '?access_token=' + access_token


class CanvasLoginWorker(ThreadRunner):
    def runner(self, knu_session: str):
        def parse_form(content: str, form_id: str) -> dict[str, str]:
            parser = BeautifulSoup(content, 'html.parser')
            form_tag = parser.find('form', {'id': form_id})
            form_content = {}
            for child in form_tag.children:
                if isinstance(child, Tag):
                    for attr in ('name', 'id'):
                        tag_type = child.get(attr)
                        if tag_type is not None:
                            break
                    else:
                        raise ValueError(f"Can't find tag type. ({child})")
                    form_content[tag_type] = child.get('value', '')
            return form_content

        def get_session_tokens(session: requests.Session) -> None:
            response = session.get(
                CANVAS_URL, headers={
                    'User-Agent': USER_AGENT,
                    'Accept': 'text/html',
                }
            )
            if response.status_code != 200:
                raise RuntimeError(f'Request failed. ({response.status_code})')

        def get_php_session_id(session: requests.Session) -> None:
            response = session.post(
                'https://lms1.knu.ac.kr/sso/business.php',
                timeout=10
            )
            if response.status_code != 200:
                raise RuntimeError(f'Request failed. ({response.status_code})')

        def get_login_info(session: requests.Session) -> dict[str, str]:
            response = session.post(
                'https://knusso.knu.ac.kr/login.html?agentId=311',
                timeout=10
            )
            if response.status_code != 200:
                raise RuntimeError(f'Request failed. ({response.status_code})')
            return parse_form(response.text, 'form-send')

        def register_session(session: requests.Session, form_content: str) -> None:
            response = session.post(
                'https://lms1.knu.ac.kr/sso/checkauth.php',
                data=form_content,
                timeout=10
            )
            if response.status_code != 200:
                raise RuntimeError(f'Request failed. ({response.status_code})')

        def get_login_data(session: requests.Session) -> tuple[dict[str, str], str]:
            def decrypt_rsa(pem_key: str, msg: str) -> str:
                key = RSA.import_key(pem_key)
                cipher = PKCS1_v1_5.new(key, SHA256)
                result = cipher.decrypt(b64decode(msg), None)
                if result is None:
                    raise RuntimeError('Failed to decode.')
                return result

            response = session.post(
                'https://lms1.knu.ac.kr/sso/agentProc.php',
                headers={
                    'User-Agent': USER_AGENT,
                    'Accept': 'text/html',
                },
                timeout=10
            )
            if response.status_code != 200:
                raise RuntimeError(f'Request failed. ({response.status_code})')

            data = parse_form(response.text, 'login_form')

            session_pass_match = re.search(
                r'loginCryption\("(.+)", "-----BEGIN RSA PRIVATE KEY-----(.+)-----END RSA PRIVATE KEY-----"\)',
                response.text
            )
            private_key = \
                f'-----BEGIN RSA PRIVATE KEY-----\n{session_pass_match[2]}\n-----END RSA PRIVATE KEY-----'
            decrypted = decrypt_rsa(private_key, session_pass_match[1])
            data['pseudonym_session[password]'] = decrypted.decode('ascii')

            return data, response.url

        def do_login(session: requests.Session, form_content: dict[str, str], prev_url: str) -> None:
            response = session.post(
                'https://canvas.knu.ac.kr/login/canvas',
                data=form_content,
                headers={
                    'User-Agent': USER_AGENT,
                    'Accept': 'text/html',
                    'Referer': prev_url,
                },
                timeout=10
            )
            if response.status_code != 200:
                raise RuntimeError(f'Request failed. ({response.status_code})')

        with requests.Session() as session:
            session.cookies.set_cookie(
                Cookie(
                    version=0,
                    name='JSESSIONID',
                    value=knu_session,
                    port=None,
                    port_specified=False,
                    domain='knusso.knu.ac.kr',
                    domain_specified=False,
                    domain_initial_dot=False,
                    path='/',
                    path_specified=True,
                    secure=True,
                    expires=None,
                    discard=True,
                    comment=None,
                    comment_url=None,
                    rest={'HttpOnly': None},
                    rfc2109=False
            ))

            get_session_tokens(session)
            get_php_session_id(session)
            login_info = get_login_info(session)
            register_session(session, login_info)

            login_data, last_url = get_login_data(session)
            do_login(session, login_data, last_url)

            return {
                'canvas_session': session.cookies[CANVAS_SESSION],
                'learningx_session': session.cookies[LEARNINGX_SESSION]
            }


class CanvasSubjectGetter(ThreadRunner):
    __URL = f'{CANVAS_URL}/api/v1/courses?include=term&per_page=50'
    __LINK_PATTERN = re.compile(r'<(.+?)>; rel="([a-z]+)"')
    __SEMESTER_PATTERN = re.compile(r'20\d{2}년 (1|2|(여름|겨울)(계절)?)학기')

    def runner(self, canvas_session: str) -> dict[str, list[tuple[str, str]]]:
        next_page = self.__URL
        last_page = ''
        result: dict[str, list[tuple[str, str]]] = {}

        while next_page:
            response = requests.get(next_page, cookies={CANVAS_SESSION: canvas_session})
            if response.status_code != 200:
                raise RuntimeError(f'Request failed. (Body: {response.text})')

            for subject in json.loads(response.text[response.text.find('['):]):
                if 'term' not in subject:
                    continue
                semester = f'{subject['term']['name'].split('학기', 1)[0]}학기'
                if self.__SEMESTER_PATTERN.fullmatch(semester):
                    result.setdefault(semester, []).append((subject['name'], subject['id']))

            if next_page == last_page:
                break

            links = {k: v for v, k in self.__LINK_PATTERN.findall(response.headers['link'])}
            next_page = links.get('next', '')
            last_page = links.get('last', '')

        return result


class CanvasFileInfoGetter(ThreadRunner):
    __LEARNINGX_URL_BASE = f'{CANVAS_URL}/learningx/api/v1'
    __LCMS_BASE_URL = 'https://lcms.knu.ac.kr'

    __LEARNINGX_MODULE_URL =\
        __LEARNINGX_URL_BASE + '/courses/{course_id}/modules?include_detail=true'
    __UNIPLAYER_INFO_BASE =\
        __LCMS_BASE_URL + '/viewer/ssplayer/uniplayer_support/content.php?content_id={content_id}'

    __LEARNINGX_BOARD_LIST_URL =\
        __LEARNINGX_URL_BASE + '/learningx_board/courses/{course_id}/boards'
    __LEARNINGX_BOARD_POSTS_URL =\
        __LEARNINGX_URL_BASE + '/learningx_board/courses/{course_id}/boards/{board_id}/posts?page={page_no}'
    __LEARNINGX_BOARD_POST_URL =\
        __LEARNINGX_URL_BASE + '/learningx_board/courses/{course_id}/boards/{board_id}/posts/{post_no}'

    __LEARNINGX_MODULE_ITEM_CONTENT_ID_PATTERN = re.compile('[0-9a-z]{13}')


    def runner(
        self, canvas_session: str, learningx_session: str, course_id: int
    ) -> tuple[LectureMaterial, ...]:
        futures: list[Future] = []
        with ThreadPoolExecutor(max(self._workers_count, 4)) as executor:
            futures.append(executor.submit(
                self.__list_module_materials, executor, learningx_session, course_id
            ))
            futures.append(executor.submit(
                self.__list_board_materials, executor, learningx_session, course_id
            ))
            return tuple(chain.from_iterable(f.result() for f in futures))

    def __list_module_materials(
        self, executor: Executor, learningx_session: str, course_id: int
    ) -> tuple[LectureMaterial, ...]:
        def list_content_ids() -> list[str]:
            # Get modules
            response = requests.get(
                self.__LEARNINGX_MODULE_URL.format(course_id=course_id),
                headers={'Authorization': f'Bearer {learningx_session}'}
            )
            if response.status_code != 200:
                raise RuntimeError(f'Request Failed (Code: {response.status_code})')

            # Extract module items
            return [
                (content_id_stripped, content_type.strip())
                for module in response.json() for items in module['module_items']
                if isinstance(items, dict)
                and isinstance(content_data := items.get('content_data', {}), dict)
                and content_data.get('opened', False)
                and isinstance(item_content_data := content_data.get('item_content_data', {}), dict)
                and isinstance(content_id := item_content_data.get('content_id', None), str)
                and self.__LEARNINGX_MODULE_ITEM_CONTENT_ID_PATTERN.fullmatch(content_id_stripped := content_id.strip())
                and isinstance(content_type := item_content_data.get('content_type', None), str)
            ]

        def get_content_material(content_info: tuple[str, str]) -> LectureMaterial:
            content_id, content_type = content_info
            match (content_type):
                case 'pdf' | 'everlec':
                    return get_uniplayer_content_material(content_id)
                case _:
                    return None

        def get_uniplayer_content_material(content_id: str) -> LectureMaterial:
            assert content_id.isascii()

            response = requests.get(self.__UNIPLAYER_INFO_BASE.format(content_id=content_id))
            if response.status_code != 200:
                raise RuntimeError(f'Request Failed. {response.status_code}')

            with warnings.catch_warnings():
                warnings.filterwarnings('ignore', category=XMLParsedAsHTMLWarning)
                parser = BeautifulSoup(response.text, 'html.parser')

            try:
                content_type = parser.select_one('content > content_playing_info > content_type').get_text(strip=True)
                match (content_type):
                    case 'sharedocs':
                        url_base = html_unescape(urllib.parse.unquote(
                            parser.select_one('content > content_playing_info > content_download_uri').get_text(strip=True)
                        ))
                        content_url = self.__LCMS_BASE_URL + url_base
                        material_type = MaterialTypes.DOCUMENT
                    case 'upf':
                        file_name = parser.select_one('story_list > story > main_media_list > main_media').get_text(strip=True)
                        url_base = parser.select_one('service_root > media > media_uri[target=all]').get_text(strip=True)
                        content_url = url_base.replace('[MEDIA_FILE]', file_name)
                        material_type = MaterialTypes.VIDEO
                    case 'video1':
                        content_url = parser.select_one('main_media > desktop > html5 > media_uri').get_text(strip=True)
                        material_type = MaterialTypes.VIDEO
                    case _:
                        raise ValueError(f'Unsupported content type: {content_type}')

                content_name_base = parser.select_one('content_metadata > title').get_text(strip=True)
                content_name = re.search(r'(<!\[CDATA\[)?(.+)(\]\]>)?', content_name_base)[2]
            except Exception as e:
                with open('parse_failed.xml', 'w', encoding='utf-8') as file:
                    file.write(response.text)
                raise e

            return LectureMaterial(
                content_name + os.path.splitext(content_url)[1],
                material_type,
                content_url
            )

        return tuple(filter(None, executor.map(get_content_material, list_content_ids())))

    def __list_board_materials(
        self, executor: Executor, learningx_session: str, course_id: int
    ) -> tuple[LectureMaterial, ...]:
        class Post(NamedTuple):
            id: str
            title: str

        class PageInfo(NamedTuple):
            items: list[Post]
            total_pages: int
            item_per_page: int

        def find_material_board_id() -> int:
            response = requests.get(
                self.__LEARNINGX_BOARD_LIST_URL.format(course_id=course_id),
                headers={'Authorization': f'Bearer {learningx_session}'}
            )
            if response.status_code != 200:
                raise RuntimeError(f'Request Failed (Code: {response.status_code})')
            for subject in response.json():
                if subject['title'] == '강의자료실':
                    return subject['id']

        def list_page(board_id: int, page: int) -> PageInfo:
            response = requests.get(
                self.__LEARNINGX_BOARD_POSTS_URL.format(
                    course_id=course_id, board_id=board_id, page_no=page
                ), headers={'Authorization': f'Bearer {learningx_session}'}
            )
            if response.status_code != 200:
                raise RuntimeError(f'Request Failed (Code: {response.status_code})')
            response_json = response.json()
            return PageInfo(
                [Post(post['id'], post['title']) for post in response_json['items']],
                response_json['pagination']['last_page'], response_json['pagination']['per_page']
            )

        def post_to_material_urls(post_id: str) -> list[LectureMaterial]:
            response = requests.get(
                self.__LEARNINGX_BOARD_POST_URL.format(
                    course_id=course_id, board_id=board_id, post_no=post_id
                ), headers={'Authorization': f'Bearer {learningx_session}'}
            )
            if response.status_code != 200:
                raise RuntimeError(f'Request Failed (Code: {response.status_code})')
            response_json = response.json()
            return [
                LectureMaterial(attachment['filename'], MaterialTypes.DOCUMENT, attachment['url'])
                for attachment in response_json['attachments']
            ]

        board_id = find_material_board_id()
        first_page = list_page(board_id, 1)
        pages = [first_page, *executor.map(list_page, repeat(board_id), range(2, first_page.total_pages + 1))]
        items = [item.id for page in pages for item in page.items]
        return tuple(chain.from_iterable(executor.map(post_to_material_urls, items)))
