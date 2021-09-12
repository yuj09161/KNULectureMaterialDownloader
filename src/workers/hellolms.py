import re

from bs4 import BeautifulSoup as bs

from .commons import HEADER, BaseRunner

LMS_URL_BASE = 'https://lms.knu.ac.kr'

EXCLUDE_TITLES = {
    '전체다운로드',
    '전체 다운로드'
}


class LoginWorker(BaseRunner):
    def runner(self, session, username, passwd):
        return session.post(
            LMS_URL_BASE + '/ilos/lo/login.acl',
            {
                'usr_id': username,
                'usr_pwd': passwd,
                'returnURL': '',
                'encoding': 'utf-8'
            },
            headers=HEADER
        ).json()


class SubjectGetter(BaseRunner):
    def runner(self, session, year, term_no):
        subjects = []

        raw_response = session.post(
            LMS_URL_BASE + '/ilos/mp/course_register_list2.acl',
            {
                'YEAR': year,
                'TERM': term_no + 1,
                'num': 1,
                'encoding': 'utf-8'
            },
            headers=HEADER
        )

        parser = bs(raw_response.text, 'html.parser')
        for subj_tag in parser.find_all('a', {'class': 'site-link'}):
            subjects.append((
                subj_tag.text.split('(')[0],
                re.search(r"eclassRoom\('(.+)'\)", subj_tag['onclick'])[1]
            ))

        return subjects


class SubjectSetter(BaseRunner):
    def runner(self, session, subj_code):
        return session.post(
            LMS_URL_BASE + '/ilos/st/course/eclass_room2.acl',
            {
                'KJKEY': subj_code,
                'returnData': 'json',
                'returnURI': '',
                'encoding': 'utf-8'
            },
            headers=HEADER
        ).json()


class FileinfoGetter(BaseRunner):
    def runner(self, session, stu_id, subj_code):
        response = session.post(
            LMS_URL_BASE + '/ilos/st/course/lecture_material_list.acl',
            {
                'start': '',
                'display': '1',
                'SCH_VALUE': '',
                'ud': stu_id,
                'ky': subj_code,
                'encoding': 'utf-8'
            },
            headers=HEADER
        )

        parser = bs(response.text, 'html.parser')
        link_tags = parser.select('tbody img[class$=_icon]')

        results = []
        for link_tag in link_tags:
            link_class = link_tag['class']
            if 'download_icon' in link_class:
                results += self.__download_files(
                    session, link_tag, stu_id, subj_code
                )
            elif 'camera_icon' in link_class:
                results += self.__download_media_files(
                    session, link_tag, stu_id, subj_code
                )

        return results

    def __list_content_files(self, session, url, body_data):
        content_response = session.post(
            LMS_URL_BASE + url, body_data, headers=HEADER
        )

        content_parser = bs(content_response.text, 'html.parser')
        return [
            (
                re.search(r'[- ]*(.+) \([0-9.]+[A-Z]?B\)', tag.text)[1],
                LMS_URL_BASE + tag['href']
            )
            for tag in content_parser.find_all('a', {'class': 'site-link'})
            if tag.text.strip() not in EXCLUDE_TITLES
        ]

    def __download_files(self, session, link_tag, stu_id, subj_code):
        content_code = \
            re.search(r"downloadClick\('(.+)'\)", link_tag['onclick'])[1]
        return self.__list_content_files(
            session, '/ilos/co/efile_list.acl', {
                'ud': stu_id,
                'ky': subj_code,
                'pf_st_flag': '2',
                'CONTENT_SEQ': content_code,
                'encoding': 'utf-8'
            }
        )

    def __download_media_files(self, session, link_tag, stu_id, subj_code):
        material_code = \
            re.search(r"cameraClick\('(.+)'\)", link_tag['onclick'])[1]
        material_response = session.get(LMS_URL_BASE + (
            '/ilos/st/course/lecture_material_view_form.acl'
            f'?ARTL_NUM={material_code}'
        ))

        content_code = re.search(
            'CONTENT_SEQ *: *"(.+)"', material_response.text
        )[1]
        return self.__list_content_files(
            session, '/ilos/co/efile_list.acl', {
                'ud': stu_id,
                'ky': subj_code,
                'pf_st_flag': '2',
                'CONTENT_SEQ': content_code,
                'encoding': 'utf-8'
            }
        )
