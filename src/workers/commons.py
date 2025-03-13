from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Iterable, NamedTuple
import os
import re

import requests

from pyside_commons import ThreadRunner, ExceptionBridge
from . import MaterialTypes


CHUNK_SIZE = 32 * (1 << 20)


HEADER_BY_TYPE = {
    MaterialTypes.DOCUMENT: {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    },
    MaterialTypes.VIDEO: {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'Accept': 'video/webm,video/ogg,video/*;q=0.9,application/ogg;q=0.7,audio/*;q=0.6,*/*;q=0.5',
        'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3',
        'Range': f'bytes=0-{CHUNK_SIZE}',
        'Connection': 'keep-alive',
        'Referer': 'https://lcms.knu.ac.kr/',
        'Sec-Fetch-Dest': 'video',
        'Sec-Fetch-Mode': 'no-cors',
        'Sec-Fetch-Site': 'cross-site',
        'Accept-Encoding': 'identity',
        'Priority': 'u=4',
        'TE': 'trailers',
    },
}


class FileDownloader(ThreadRunner):
    def runner(self, selected_files: Iterable[tuple[str, MaterialTypes, str, Callable[[str], Any]]], destination_dir: str):
        class Range(NamedTuple):
            start: int
            end: int
            total_length: int

        def extract_range_from_body(response_headers: dict[str, str]):
            keys = {k.lower(): k for k in response_headers.keys()}
            length_str = response_headers[keys['content-range']]
            length_match = re.search('([a-z]+) (\\d+)-(\\d+)/(\\d+)', length_str)
            if length_match is None or length_match.group(1).lower() != 'bytes':
                raise ValueError(f'Illegal length header value. ({length_str})')
            return Range(int(length_match.group(2)), int(length_match.group(3)), int(length_match.group(4)))

        def download_file(name: str, type: MaterialTypes, url: str, result_callback: Callable[[str], Any]):
            response = requests.get(url, headers=HEADER_BY_TYPE[type])
            if response.status_code == 200:
                with open(f'{destination_dir}/{name}', 'wb') as file:
                    file.write(response.content)
                result_callback('성공')
                return True, '성공'
            elif response.status_code == 206:
                target = f'{destination_dir}/{name}'
                destination = f'{target}.part'
                with open(destination, 'wb') as file:
                    file.write(response.content)
                with open(destination, 'ab') as file:
                    while True:
                        range_ = extract_range_from_body(response.headers)
                        if (range_.end >= range_.total_length - 1):
                            break
                        result_callback(f'{round(range_.end / range_.total_length * 100, 1)}%')
                        response = requests.get(url, headers=HEADER_BY_TYPE[type] | {'Range': f'bytes={range_.end + 1}-{range_.end + CHUNK_SIZE + 1}'})
                        if response.status_code != 206:
                            ExceptionBridge().warning('다운로드 실패', f'파일 다운로드 실패\n이름: {name}\n응답 Code: {response.status_code}')
                            result_callback(f'실패 (Code: {response.status_code})')
                            return False, f'실패 (Code: {response.status_code})'
                        file.write(response.content)
                os.rename(destination, target)
                result_callback('성공')
                return True, '성공'
            else:
                ExceptionBridge().warning('다운로드 실패', f'파일 다운로드 실패\n이름: {name}\n응답 Code: {response.status_code}')
                result_callback(f'실패 (Code: {response.status_code})')
                return False, f'실패 (Code: {response.status_code})'

        with ThreadPoolExecutor(max(self._workers_count, 4)) as executor:
            return tuple(executor.map(download_file, *zip(*selected_files)))
