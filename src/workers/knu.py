from bs4 import BeautifulSoup
import requests

from pyside_commons import ThreadRunner


class KNUIdPwLoginWorker(ThreadRunner):
    LOGIN_URL = 'https://knusso.knu.ac.kr/authentication/idpw/loginProcess'

    def runner(self, id: str, pw: str):
        try:
            response = requests.post(
                self.LOGIN_URL,
                data={'id': id, 'pw': pw, 'agentId': '2'}, timeout=10
            )
        except requests.exceptions.Timeout:
            return {'success': False, 'code': 'Timeout', 'message': '로그인 실패'}
        if response.status_code != 200:
            raise RuntimeError(f'Request failed. (code: {response.status_code} | body: {response.text})')
        parser = BeautifulSoup(response.text, 'html.parser')
        send_form = parser.select_one('form#form-send')
        if send_form.select_one('input#reTry')['value'].upper() != 'N':
            return {
                'success': False,
                'code': parser.select_one('form#form-send > input#resultCode')['value'],
                'message': parser.select_one('form#form-send > input#resultMessage')['value'],
            }
        return {'success': True, 'knu_session': response.cookies['JSESSIONID']}

class KNULoginPushSender(ThreadRunner):
    NOTIFICATION_URL = 'https://appfn.knu.ac.kr/login/notification'

    def runner(self, id: str):
        try:
            response = requests.post(
                self.NOTIFICATION_URL,
                json={'type': 'login', 'userId': id},
                timeout=10
            )
        except requests.exceptions.Timeout:
            return {'success': False, 'code': 'Timeout', 'message': '로그인 알림 전송 실패'}
        if response.status_code != 200:
            raise RuntimeError(f'Request failed. (Code: {response.status_code} | Body: {response.text})')
        response_json = response.json()
        if not response_json['success']:
            return {'success': False, 'code': response.json()['code'], 'message': response.json()['msg']}
        if not response_json['data']['success']:
            return {'success': False, 'code': '-', 'message': '로그인 알림 전송 실패'}
        return {'success': True, 'trial': response_json['data']['trId']}

class KNUPushLoginWorker(ThreadRunner):
    REQUEST_URL = 'https://knusso.knu.ac.kr/authentication/raonuaf/loginProcess'

    def runner(self, id: str, trial: str):
        try:
            response = requests.post(
                self.REQUEST_URL,
                data={
                    'agentId': '2',
                    'siteId': 'SIT01KNUAC0000000000',
                    'svcId': 'SVC01SIT01KNUAC00000',
                    'svcTrId': trial,
                    'loginId': id,
                },
                timeout=10
            )
        except requests.exceptions.Timeout:
            return {'success': False, 'code': 'Timeout', 'message': '로그인 실패'}
        if response.status_code != 200:
            raise RuntimeError(f'Request failed. (code: {response.status_code} | body: {response.text})')
        parser = BeautifulSoup(response.text, 'html.parser')
        send_form = parser.select_one('form#form-send')
        if send_form.select_one('input#reTry')['value'].upper() != 'N':
            return {
                'success': False,
                'code': parser.select_one('form#form-send > input#resultCode')['value'],
                'message': parser.select_one('form#form-send > input#resultMessage')['value'],
            }
        return {'success': True, 'knu_session': response.cookies['JSESSIONID']}
