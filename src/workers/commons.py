from multiprocessing import cpu_count

from pyside_commons import ThreadRunner


CPU_CNT = cpu_count()

HEADER = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/99.0.7113.93 Safari/537.36'
    )
}


class FileDownloader(ThreadRunner):
    def runner(self, session, selected_files, dst):
        results = []
        for name, url in selected_files:
            response = session.get(url, headers=HEADER)
            if response.status_code == 200:
                results.append((True, '성공'))
                with open(dst + name, 'wb') as file:
                    file.write(response.content)
            else:
                results.append((False, '실패'))
        return results
