import re
import json
import urllib.parse
import xml.etree.ElementTree as et
from typing import Union
from operator import add
from functools import reduce
from itertools import repeat, chain
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor

import requests
from bs4 import BeautifulSoup as bs

from pyside_commons import ThreadRunner


CANVAS_URL = 'https://canvas.knu.ac.kr'


def _join_url_token(
    url: str, access_token: str, options: Iterable = None
) -> str:
    if options:
        return url + '?access_token=' + access_token + '&' + '&'.join(options)
    return url + '?access_token=' + access_token


class SubjectGetter(ThreadRunner):
    __SUBJECT_GET_URL = CANVAS_URL + '/api/v1/courses'

    def runner(
        self, year: str, semester: str, access_token: str
    ) -> Union[list, str]:
        """
        Get subjects list.

        Args:
            session (aiohttp.ClientSession): The session to use.
            year (str): The year to get. (in YYYY년)
            semester (str): The semester to get. (in S학기)
            access_token(str): The token generated from account setting.

        Returns:
            list:
                Return this type when getting subject is successed.
                Contains tuple of (subject name, canvas course id).
            str:
                Return this type when getting subject is failed.
                Equal to error message from response.
        """
        response = requests.get(_join_url_token(
            self.__SUBJECT_GET_URL, access_token, ('include=term',)
        ))
        if response.status_code == 200:
            return [
                (subject['name'], subject['id'])
                for subject in response.json()
                if subject['term']['name'] == f'{year} {semester}'
            ]
        else:
            return response.json()['errors'][0]['message']


class FileinfoGetter(ThreadRunner):
    __MODULES_URL = CANVAS_URL + '/api/v1/courses/{}/modules'
    __EXTERNAL_TOOL_URL = (
        CANVAS_URL
        + '/api/v1/courses/{}/external_tools'
        + '/sessionless_launch'
    )
    __RESOURCE_TOOL_ID = '2'
    __RESOURCE_DB_URL = \
        CANVAS_URL + '/learningx/api/v1/courses/{}/resources_db'
    __CONTENTS_TEMPLATE = 'https://lcms.knu.ac.kr/em/{}'
    __CONTENTS_BASE_URL = 'https://lcms.knu.ac.kr'

    def runner(
        self, access_token: str, course_id: int
    ) -> Union[list, str]:
        """
        Get material files within the subject.

        Args:
            session (aiohttp.ClientSession): The session to use.
            access_token(str): The token generated from account setting.
            course_id(int): The canvas course id (returned from SubjectGetter).

        Returns:
            list:
                Return this type when getting subject is successed.
                Contains tuple of (Filename with extension, Download URL).
            str:
                Return this type when getting subject is failed.
                Equal to error message from response.
        """
        with ThreadPoolExecutor(self._workers_count) as executor:
            modules_results = self.__material_extractor(
                access_token, course_id, executor
            )
            resource_results = self.__resource_extractor(
                access_token, course_id, executor
            )

        return [
            (name, url)
            for _, name, url in sorted(reduce(
                add, chain(modules_results, resource_results)
            ))
            if not name.startswith('Error')
        ]

    # Common functions
    def __lcms_extractor(self, rid: str) -> tuple:
        # Get contents info
        c_response = requests.get(
            self.__CONTENTS_TEMPLATE.format(rid)
        )
        ci_url_match = re.search(r"var contentUri = '(.+)';", c_response.text)
        if ci_url_match:
            ci_response = requests.get(
                self.__CONTENTS_BASE_URL + ci_url_match[1]
            )

            # Get contents download url and extension
            download_url = self.__CONTENTS_BASE_URL + (
                et.fromstring(ci_response.text)
                .find('.//content_download_uri').text
            )
            extension = '.' + urllib.parse.parse_qs(
                urllib.parse.urlparse(download_url).query
            )['file_subpath'][0].rsplit('.', 1)[1]

            return download_url, extension

        c_parser = bs(c_response.text, 'html.parser')
        if c_parser.find('button', {'id': 'content_download_btn'}):
            download_url = re.search(
                "download_iframe.attr\\('src', \"(.+)\"\\);",
                c_response.text
            )[1]
            return download_url, ''

        print(f'Unexpected page: {rid}')
        return 'Error', None
    # end common func

    # Material related functions
    def __material_extractor(
        self, access_token: str, course_id: int, executor: ThreadPoolExecutor
    ):
        response = requests.get(_join_url_token(
            self.__MODULES_URL.format(course_id), access_token
        ))
        if response.status_code != 200:
            return response.json()['errors'][0]['message']
        works = [
            (k, module['items_url'])
            for k, module in enumerate(response.json())
        ]

        return executor.map(
            self.__itemgetter, works, repeat(access_token)
        )

    def __itemgetter(self, work_info: tuple, access_token: str) -> list:
        def canvas_api_getter(url: str) -> tuple:
            response = requests.get(_join_url_token(url, access_token))
            if response.status_code != 200:
                return (
                    False, json.loads(
                        response.text.rsplit(';', 1)[-1]
                    )['errors'][0]['message']
                )

            return (True, response.json())

        work_id, m_url = work_info
        results = []

        # Query an module item, gets resources list.
        i_success, i_result = canvas_api_getter(m_url)
        if not i_success:
            return ((work_id, 'Error while querying item', i_result),)

        # Query resources
        for resource in i_result:
            r_url = resource.get('url', '')
            if not r_url:
                continue

            # Query resource information
            r_success, r_result = canvas_api_getter(r_url)
            if not r_success:
                results.append((
                    work_id, 'Error while querying resource', r_result
                ))
                continue

            # Parse resource information
            rtype, rid = (
                r_result['external_tool_tag_attributes']['url']
                .rsplit('/', 2)[1:]
            )
            if rtype != 'contents':
                continue

            download_url, ext = self.__lcms_extractor(rid)

            results.append((
                work_id, r_result['name'] + ext, download_url
            ))

        return results
    # end material func

    # Resource related functions
    def __resource_extractor(
        self, access_token: str, course_id: int, executor: ThreadPoolExecutor
    ):
        def worker(work_info: tuple) -> list:
            work_id, rname, rid = work_info
            results = []

            download_url, ext = self.__lcms_extractor(rid)
            results.append((work_id, rname + ext, download_url))

            return results

        # Get LearningX api token
        session = requests.Session()
        response = session.get(
            _join_url_token(
                self.__EXTERNAL_TOOL_URL.format(course_id),
                access_token, ('id=' + self.__RESOURCE_TOOL_ID,)
            )
        )
        # print(response.json()['url'])
        response = session.get(response.json()['url'])
        # print(response.text)
        extracted_data = {
            tag['name']: tag['value']
            for tag in bs(response.text, 'html.parser').select('form input')
        }
        response = session.post(
            'https://canvas.knu.ac.kr/learningx/lti/courseresource',
            data=extracted_data
        )
        # print(json.dumps(extracted_data, indent=4, ensure_ascii=False))
        # print(
        #     session.cookies.get('xn_api_token', None),
        #     session.cookies, sep='\n'
        # )
        session.headers.update({
            'Authorization': f"Bearer {session.cookies['xn_api_token']}"
        })
        # end token
        response = session.get(
            self.__RESOURCE_DB_URL.format(course_id),
        )
        works = [
            (k, resource['title'], resource['commons_content']['content_id'])
            for k, resource in enumerate(response.json())
        ]

        return executor.map(worker, works)
    # end resource func
