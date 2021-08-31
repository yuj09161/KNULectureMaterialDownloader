from PySide6.QtCore import QThread, Signal
from bs4 import BeautifulSoup as bs

from constants import CPU_CNT


HEADER = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/99.0.7113.93 Safari/537.36'
    )
}
LMS_URL_BASE = 'https://lms.knu.ac.kr'

EXCLUDE_TITLES = {
    '전체다운로드',
    '전체 다운로드'
}


class BaseRunner(QThread):
    ended = Signal(object)

    def __init__(self, parent, runner_cnt=0, runner=None):
        super().__init__(parent)

        self.runner_cnt = (
            runner_cnt if runner_cnt else min(CPU_CNT * 2, 16)
        )
        if runner:
            self._workers = [runner(self) for _ in range(self.runner_cnt)]

    def start(self, *args, **kwargs):
        # pylint: disable=attribute-defined-outside-init
        try:
            self.ended.disconnect()
        except RuntimeError:
            pass
        if 'end' in kwargs:
            self.ended.connect(kwargs.pop('end'))
        priority = kwargs.pop('priority', QThread.LowPriority)

        self.__args = args
        self.__kwargs = kwargs

        super().start(priority)

    def run(self):
        self.ended.emit(self.runner(*self.__args, **self.__kwargs))


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
        subject_names = []
        subject_codes = []

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
            subject_codes.append(subj_tag.text.split('(')[0])
            subject_names.append(
                subj_tag['onclick'].split("eclassRoom('")[1].split("');")[0],
            )

        return subject_names, subject_codes


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


class FileDownloader(BaseRunner):
    def runner(self, session, selected_files, dst):
        results = []
        for name, url in selected_files:
            response = session.get(url, headers=HEADER)
            if response.status_code == 200:
                results.append('성공')
                with open(dst + name, 'wb') as file:
                    file.write(response.content)
            else:
                results.append('실패')
        return results
