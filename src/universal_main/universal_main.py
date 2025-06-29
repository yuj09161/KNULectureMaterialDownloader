"""The package install automation tool.
"""

import os
import sys
import shutil
import zipfile
import tempfile
import subprocess
from importlib import import_module
from typing import Iterable, List

from .universal_constants import (
    ENCODING, IS_WINDOWS, PROGRAM_DIR, IS_ZIPFILE, ZIPAPP_FILE
)


FILE_DIR = os.path.abspath(os.path.dirname(__file__)) + '/'


Qt = None
QIcon = None
QApplication = None
QVBoxLayout = None
QLabel = None
QSplashScreen = None
_Splash = None


def _check_py37() -> bool:
    """
    Check Python version is >= 3.7.

    Returns:
        bool: If version < 3.7, return True. Otherwise, return False.
    """
    if sys.version_info < (3, 7):
        print(
            'This program needs Python >= 3.7.',
            'Please upgrade Python version and try again.',
            sep='\n'
        )
        return True
    return False


def _nt_run_cmd(args: List[str]) -> subprocess.CompletedProcess:
    """
    Call subprocess.run with given args.

    Call subprocess.run
    with stdout/stderr PIPE redirect
    and CREATE_NO_WINDOW flag.

    Args:
        args (List[str]): The command to run.

    Returns:
        subprocess.CompletedProcess: The ran result.
    """
    return subprocess.run(
        args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NO_WINDOW, check=False
    )


def _posix_run_cmd(args: List[str]) -> subprocess.CompletedProcess:
    """
    Call subprocess.run with given args.

    Call subprocess.run with stdout/stderr PIPE redirect.

    Args:
        args (List[str]): The command to run.

    Returns:
        subprocess.CompletedProcess: The ran result.
    """
    return subprocess.run(
        args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False
    )


if IS_WINDOWS:
    run_cmd = _nt_run_cmd
else:
    run_cmd = _posix_run_cmd


def _check_to_install(requirements: Iterable[str]) -> List[str]:
    """
    Check which packages need to be installed.

    Args:
        requirements (Iterable[str]):
            The pypi package names that must be installed.

    Returns:
        List[str]: The package names.
    """
    installed = run_cmd(['pip', 'list']).stdout.decode(ENCODING)
    return [
        package for package in requirements
        if not package + ' ' in installed
    ]


def _zipapp_package_installer() -> int:
    """
    The package checker and installer (Python zipapp version.)

    Returns:
        int: The return code from popened process.
    """
    with zipfile.ZipFile(ZIPAPP_FILE) as main_zip:
        with main_zip.open('requirements.txt', 'r') as requirements_file:
            requirements = requirements_file.read().decode('utf-8')
        to_install = _check_to_install(filter(None, requirements.splitlines()))

        if not to_install:
            return 0

        with tempfile.TemporaryDirectory() as tmp_dir:
            installer_path = tmp_dir + '/package_installer.py'

            for name in main_zip.namelist():
                if name.endswith('package_installer.py'):
                    extracted_path = main_zip.extract(name, tmp_dir)
                    break
            if extracted_path != installer_path:
                os.rename(extracted_path, installer_path)

            if IS_WINDOWS:
                curses_dir = tmp_dir + '/wincurses'
                wincurses_dir = os.path.dirname(installer_path) + '/wincurses/'
                os.mkdir(curses_dir)
                major, minor = sys.version_info[:2]
                with main_zip.open(
                    wincurses_dir
                    + f"wincurses/curses-cp{major}{minor}_"
                    + '64.whl' if sys.maxsize == 2 ** 63 - 1 else '32.whl'
                    , 'rb'
                ) as curses_pyd:
                    for name in curses_pyd.namelist():
                        if name.endswith('.pyd'):
                            curses_pyd.extract(name, curses_dir)

            return subprocess.run([
                'py' if IS_WINDOWS else sys.executable,
                installer_path, *to_install
            ], check=False).returncode


def _normal_package_checker() -> int:
    """
    The package checker and installer (non-zipapp version.)

    Returns:
        int: The return code from popened process.
    """
    with open(
        PROGRAM_DIR + 'requirements.txt', 'r', encoding='utf-8'
    ) as file:
        requirements = file.read()
    to_install = _check_to_install(filter(None, requirements.splitlines()))

    if not to_install:
        return 0

    if IS_WINDOWS:
        with tempfile.TemporaryDirectory() as tmp_dir:
            shutil.copy(FILE_DIR + 'package_installer.py', tmp_dir)

            curses_dir = tmp_dir + '/wincurses'
            os.mkdir(curses_dir)
            major, minor = sys.version_info[:2]
            with zipfile.ZipFile(
                FILE_DIR
                + f"wincurses/curses-cp{major}{minor}_"
                + '64.whl' if sys.maxsize == 2 ** 63 - 1 else '32.whl'
            ) as curses_pyd:
                for name in curses_pyd.namelist():
                    if name.endswith('.pyd'):
                        curses_pyd.extract(name, curses_dir)

            return subprocess.run([
                'py' if IS_WINDOWS else sys.executable,
                tmp_dir + '/package_installer.py', *to_install
            ], check=False).returncode

    return subprocess.run([
        'py' if IS_WINDOWS else sys.executable,
        FILE_DIR + 'package_installer.py', *to_install
    ], check=False).returncode


def main(main_module_name: str, main_func_name: str):
    """
    Check & install packages, and run main function.

    Args:
        main_module_name (str):
            The module that main function exists.
        main_func_name (str):
            The name of main function.
            It will be called by this function
            if installer successfully executed.
    """
    if _check_py37():
        return

    if IS_ZIPFILE:
        return_code = _zipapp_package_installer()
    else:
        return_code = _normal_package_checker()

    if return_code == 0:
        main_module = import_module(main_module_name)
        return getattr(main_module, main_func_name)()


def _check_imports() -> bool:
    """
    Import some PySide6 classes if the classes not imported.

    Will import these classes:
    PySide6.QtCore.Qt
    PySide6.QtGui.QIcon
    PySide6.QtWidgets.QApplication
    PySide6.QtWidgets.QVBoxLayout
    PySide6.QtWidgets.QLabel

    Returns:
        bool: If import failed, return True. Otherwise, return False.
    """
    try:
        # pylint: disable = global-statement
        # pylint: disable = redefined-outer-name
        # pylint: disable = import-outside-toplevel
        global Qt
        global QIcon
        global QApplication
        global QVBoxLayout
        global QLabel
        global QSplashScreen
        global _Splash
        if Qt is None:
            from PySide6.QtCore import Qt
        if QIcon is None:
            from PySide6.QtGui import QIcon
        if QApplication is None:
            from PySide6.QtWidgets import QApplication
        if QVBoxLayout is None:
            from PySide6.QtWidgets import QVBoxLayout
        if QLabel is None:
            from PySide6.QtWidgets import QLabel
        if QSplashScreen is None:
            from PySide6.QtWidgets import QSplashScreen
        if _Splash is None:
            class _Splash(QSplashScreen):
                def __init__(self, app, splash_text):
                    # pylint: disable = not-callable
                    super().__init__()
                    x, y = app.screens()[0]\
                        .availableGeometry().size().toTuple()
                    self.setGeometry(x // 2 - 200, y // 2 - 100, 400, 300)
                    self.setFixedSize(400, 200)

                    self.vl = QVBoxLayout(self)

                    self.lb = QLabel(self)
                    self.lb.setAlignment(Qt.AlignCenter)
                    self.lb.setText(splash_text)
                    self.lb.setStyleSheet("font-size: 30px")
                    self.vl.addWidget(self.lb)
    except ImportError:
        return True
    return False


def pyside6_splash_main(
    main_module_name: str,
    main_func_name: str,
    app_name: str,
    splash_text: str,
    pre_main_name: str = ''
):
    """
    Splash screen & intall packages.
    1. Show PySide6 splash
    2. Check & install packages
    3. Hide splash
    4. Then run the main function.

    Text of splash screen is read from splash.txt at root directory.

    Args:
        main_module_name (str):
            The module that main function exists.
        main_func_name (str):
            The name of main function.
            It will be called by this function
            if installer successfully executed.
        splash_text (str):
            The text displayed to splash screen.
        pre_main_name (str, optional):
            Function that must be called before main function run.
            Return value of function will be used
                as second argument of main function.
    """
    if _check_py37():
        return

    # pylint: disable = not-callable
    if _check_imports():  # When PySide6 is not installed
        # Check missing packages and install (with PySide6)
        if IS_ZIPFILE:
            return_code = _zipapp_package_installer()
        else:
            return_code = _normal_package_checker()

        # Create Qt application & Show splash
        app = QApplication()
        app.setWindowIcon(QIcon(PROGRAM_DIR + 'logo.png'))
        app.setApplicationDisplayName(app_name)

        splash = _Splash(app, splash_text)
        splash.show()

    else:  # When PySide6 is installed
        # Create Qt application & Show splash
        app = QApplication()
        app.setWindowIcon(QIcon(PROGRAM_DIR + 'logo.png'))
        app.setApplicationDisplayName(app_name)

        splash = _Splash(app, splash_text)
        splash.show()

        # Check another missing packages
        if IS_ZIPFILE:
            return_code = _zipapp_package_installer()
        else:
            return_code = _normal_package_checker()

    if return_code == 0:
        main_module = import_module(main_module_name)
        if pre_main_name:
            res = getattr(main_module, pre_main_name)()
            splash.hide()
            return getattr(main_module, main_func_name)(app, res)
        else:
            splash.hide()
            return getattr(main_module, main_func_name)(app)
    else:
        splash.hide()
