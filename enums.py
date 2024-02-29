from enum import Enum


class ExitCodes(Enum):
    SUCCESS = 0
    MISSING_REQUIREMENTS = 2
    VENV_CREATION_ERROR = 3
