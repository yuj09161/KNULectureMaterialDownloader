import json
import urllib.parse
import xml.etree.ElementTree as et
from typing import Union
from operator import add
from functools import reduce
from itertools import repeat
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor

import requests

from .commons import BaseRunner


CANVAS_URL = 'https://canvas.knu.ac.kr'


def _join_url_token(
    url: str, access_token: str, options: Iterable = None
) -> str:
    if options:
        return url + '?access_token=' + access_token + '&' + '&'.join(options)
    return url + '?access_token=' + access_token


class SubjectGetter(BaseRunner):
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


class FileinfoGetter(BaseRunner):
    __MODULES_URL = CANVAS_URL + '/api/v1/courses/{}/modules'
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
        response = requests.get(
            _join_url_token(
                self.__MODULES_URL.format(course_id), access_token
            )
        )  # Query modules
        if response.status_code != 200:
            return response.json()['errors'][0]['message']

        works = [
            (k, module['items_url'])
            for k, module in enumerate(response.json())
        ]

        with ThreadPoolExecutor(
            min(self._runner_cnt, len(works))
        ) as executor:
            results = executor.map(
                self.__itemgetter, works, repeat(access_token)
            )

        return [
            (name, url)
            for _, name, url in sorted(reduce(add, results))
            if not name.startswith('Error')
        ]

    def __canvas_api_getter(self, url: str, access_token: str) -> tuple:
        response = requests.get(_join_url_token(url, access_token))
        if response.status_code != 200:
            return (
                False, json.loads(
                    response.text.rsplit(';', 1)[-1]
                )['errors'][0]['message']
            )

        return (True, response.json())

    def __itemgetter(self, work_info: tuple, access_token: str) -> list:
        work_id, m_url = work_info
        results = []

        # Query an module item, gets resources list.
        i_success, i_result = self.__canvas_api_getter(
            m_url, access_token
        )
        if not i_success:
            return ((work_id, 'Error while querying item', i_result),)

        # Query resources
        for resource in i_result:
            r_url = resource.get('url', '')
            if not r_url:
                continue

            # Query resource information
            r_success, r_result = self.__canvas_api_getter(
                r_url, access_token
            )
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

            # Get contents info
            c_response = requests.get(
                self.__CONTENTS_TEMPLATE.format(rid)
            )
            ci_url = self.__CONTENTS_BASE_URL + (
                c_response.text
                .split("var contentUri = '", 1)[1]
                .split("';", 1)[0]
            )
            ci_response = requests.get(ci_url)

            # Get contents download url and extension
            download_url = self.__CONTENTS_BASE_URL + (
                et.fromstring(ci_response.text)
                .find('.//content_download_uri').text
            )
            extension = '.' + urllib.parse.parse_qs(
                urllib.parse.urlparse(download_url).query
            )['file_subpath'][0].rsplit('.', 1)[1]
            results.append((
                work_id, r_result['name'] + extension, download_url
            ))

        return results
