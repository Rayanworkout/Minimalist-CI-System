from enum import Enum


class ExitCodes(Enum):
    SUCCESS = 0
    ERROR_EXIT = 1
    MISSING_REQUIREMENTS = 2
    MISSING_TEST_FILE = 3
    VENV_CREATION_ERROR = 4
