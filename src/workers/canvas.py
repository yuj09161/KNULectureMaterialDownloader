import os

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import (
    WebDriverException, TimeoutException
)

from .commons import BaseRunner


TIMEOUT = 30

# class names, selectors, urls
USERID_ID = 'login_user_id'
PASSWD_ID = 'login_user_password'
SUBJECT_LINK_XPATH = "//a[@class='ic-DashboardCard__link']"
SUBJECT_NAME_XPATH = './div/h3/span'
MATERIAL_SUFFIX = '/external_tools/2'

# Default binaries (Defaults to None, for debug)
# CURRENT_DIR = os.path.dirname(os.path.abspath(__file__)) + '/'
# DEFAULT_FIREFOX_DRIVER = CURRENT_DIR + geckodriver.exe
DEFAULT_FIREFOX_BINARY = None
# DEFAULT_CHROME_DRIVER = CURRENT_DIR + chromedriver.exe
# DEFAULT_CHROME_BINARY = None
DEFAULT_FIREFOX_DRIVER = 'C:/User Programs/geckodriver.exe'
DEFAULT_CHROME_DRIVER = 'C:/User Programs/chromedriver.exe'
DEFAULT_CHROME_BINARY = 'C:/User Programs/Chromium/bin/chrome.exe'


# From selenium source at documation
# License: Apache license

# To prevent AttributeError
def any_of(*conditions):
    """ An expectation that any of multiple expected conditions is true.
    Equivalent to a logical 'OR'.
    Returns results of the first matching condition, or False if none do. """
    def any_of_condition(driver):
        for expected_condition in conditions:
            try:
                result = expected_condition(driver)
                if result:
                    return result
            except WebDriverException:
                pass
        return False
    return any_of_condition

expected_conditions.any_of = any_of  # noqa: E305
# end from selenium


class FirefoxStarter(BaseRunner):
    class __Firefox(webdriver.Firefox):
        def __init__(
            self,
            driver_location: str = DEFAULT_FIREFOX_DRIVER,
            binary_location: str = DEFAULT_FIREFOX_BINARY
        ):
            profile = webdriver.FirefoxProfile()
            profile.set_preference("dom.popup_maximum", 0)

            options = webdriver.FirefoxOptions()
            if binary_location is not None:
                options.binary_location = binary_location

            super().__init__(
                profile,
                options=options,
                executable_path=driver_location,
                service_log_path=os.devnull
            )
            self.minimize_window()

    def runner(
        self,
        driver_location: str = DEFAULT_FIREFOX_DRIVER,
        binary_location: str = DEFAULT_FIREFOX_BINARY
    ) -> webdriver.Firefox:
        """
        Start & connect to firefox browser.

        Args:
            driver_location (str):
                The path of driver.
                If not specified, defaults to [current_dir]/geckodriver.exe.
            binary_location (str):
                The path of Firefox binary.
                If not specified, defaults to system default.

        Returns:
            webdriver.Firefox: The instance of Firefox webdriver.
        """
        driver = self.__Firefox(driver_location, binary_location)
        return driver, WebDriverWait(driver, TIMEOUT)


class ChromeStarter(BaseRunner):
    class __Chrome(webdriver.Chrome):
        def __init__(
            self,
            driver_location: str = DEFAULT_CHROME_DRIVER,
            binary_location: str = DEFAULT_CHROME_BINARY
        ):
            options = webdriver.ChromeOptions()
            options.add_experimental_option(
                'excludeSwitches', ['enable-logging']
            )
            if binary_location is not None:
                options.binary_location = binary_location

            super().__init__(
                driver_location,
                options=options
            )
            self.minimize_window()

    def runner(
        self,
        driver_location: str = DEFAULT_CHROME_DRIVER,
        binary_location: str = DEFAULT_CHROME_BINARY
    ) -> webdriver.Chrome:
        """
        Start & connect to chrome browser.

        Args:
            driver_location (str):
                The path of driver.
                If not specified, defaults to [current_dir]/chromedriver.exe.
            binary_location (str):
                The path of Chrome binary.
                If not specified, defaults to system default.

        Returns:
            webdriver.Chrome: The instance of Chrome webdriver.
        """
        driver = self.__Chrome(driver_location, binary_location)
        return driver, WebDriverWait(driver, TIMEOUT)


class WebdriverQuitter(BaseRunner):
    def runner(self, driver):
        """
        Call quit() method of given webdriver

        Args:
            driver: The instance of Any WebDriver to quit.
        """
        driver.quit()


class LoginWorker(BaseRunner):
    def runner(self, driver, wait, url: str, username: str, passwd: str):
        """
        Login to the canvas.

        Args:
            driver:
                The instance of Any WebDriver.
                (Tested with FirefoxDriver and ChromeDriver)
            wait (selenium.webdriver.support.ui.WebDriverWait):
                The wait of given driver.
            url (str): Url of the login page.
            username (str): The name of user.
            passwd (str): The passwd of user.
        """
        driver.get(url)
        wait.until(expected_conditions.presence_of_element_located(
            ('id', USERID_ID)
        ))
        id_input = driver.find_element_by_id(USERID_ID)
        id_input.send_keys(username)
        pass_input = driver.find_element_by_id(PASSWD_ID)
        pass_input.send_keys(passwd)
        pass_input.send_keys(Keys.RETURN)

        try:
            elem = wait.until(expected_conditions.any_of(
                expected_conditions.presence_of_element_located(
                    ('id', 'application')
                ),
                expected_conditions.presence_of_element_located(
                    ('xpath', "//div[@class='error")
                )
            ))
        except TimeoutException:
            return '시간 초과'

        if elem.get_attribute('id') == 'application':
            return None
        if elem.get_attribute('class') == 'error':
            return elem.find_element_by_xpath("./div[@class='box']/p").text
        return '알 수 없는 오류'


class SubjectGetter(BaseRunner):
    def runner(self, driver, wait, url: str, year: int, semester: str):
        """
        Get the subjects from given url (or current page if url is not given).
        Must be called after successful login.

        Args:
            driver:
                The instance of Any WebDriver.
                (Tested with FirefoxDriver and ChromeDriver)
            wait (selenium.webdriver.support.ui.WebDriverWait):
                The wait of given driver.
            url (str): Page to get subjects.
            year (int): The year to get subjects (YYYY).
            semester (str): The semester to get subjects (in word).
        """
        semester_str = f'{year}년 {semester}'

        driver.get(url)

        try:
            table = wait.until(
                expected_conditions.presence_of_element_located(
                    ('id', 'my_courses_table')
                )
            )
        except TimeoutException:
            return '시간 초과'

        subjects = []
        for row in (
                table
                .find_element_by_tag_name('tbody')
                .find_elements_by_tag_name('tr')
                ):
            link_tag = row.find_element_by_xpath(
                "./td[contains(@class, 'course-list-course-title-column')]/a"
            )
            subj_name = link_tag.get_attribute('title')
            subj_url = link_tag.get_attribute('href')
            subj_semester = row.find_element_by_xpath(
                "./td[contains(@class, 'course-list-term-column')]"
            ).text
            if subj_semester == semester_str:
                subjects.append((subj_name, subj_url))

        return subjects


class FileinfoGetter(BaseRunner):
    def runner(self, driver, wait, url: str):
        """
        Get material files from given url.

        Args:
            driver:
                The instance of Any WebDriver.
                (Tested with FirefoxDriver and ChromeDriver)
            wait (selenium.webdriver.support.ui.WebDriverWait):
                The wait of given driver.
            url (str): The url of subject home to get list of files.
        """
