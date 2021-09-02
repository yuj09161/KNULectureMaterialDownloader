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
                subj_tag['onclick'].split("eclassRoom('")[1].split("');")[0]
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
        rows = parser.find('tbody').find_all('img', {'class': 'download_icon'})

        results = []
        for row in rows:
            row_code = \
                row['onclick'].split("downloadClick('")[1].split("')")[0]
            row_response = session.post(
                LMS_URL_BASE + '/ilos/co/list_file_list2.acl',
                {
                    'ud': stu_id,
                    'ky': subj_code,
                    'pf_st_flag': '2',
                    'CONTENT_SEQ': row_code,
                    'encoding': 'utf-8'
                },
                headers=HEADER
            )

            row_parser = bs(row_response.text, 'html.parser')
            results += [
                (
                    tag.text.strip(),
                    (
                        'https://lms.knu.ac.kr'
                        + tag['onclick']
                        .split("location.href='")[1]
                        .split("'")[0]
                    )
                )
                for tag in row_parser.find_all('a', {'class': 'site-link'})
                if tag.text.strip() not in EXCLUDE_TITLES
            ]

        return results
