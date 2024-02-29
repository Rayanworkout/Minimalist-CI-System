import subprocess
from enums import ExitCodes


def clone_or_pull_project(project_url: str) -> bool:
    """Clone or pull latest changes of a project.

    params:
        project_url: github project url as string, like this: https://github.com/username/project

    The function calls a bash script to perform the operation, with 2 args: project url and project name.

    Returns True if script execution went well, otherwise False.

    """

    # Extract project name from URL, last index after last /
    project_name = project_url.split("/")[-1]

    return_code = subprocess.call(
        ["bash", "bash_scripts/clone_or_update_project.sh", project_name, project_url]
    )

    # Exit code 0 == success
    if return_code == ExitCodes.SUCCESS:
        return True
    else:
        return False


def run_test_script(project_name: str, test_file_name: str) -> tuple[(ExitCodes, str)]:
    """
    Runs a bash script that creates a venv and installs project dependencies.

    The bash script then calls another bash script that run tests.

    Returns tuple with (success: Boolean, optional error message)

    Exit codes:
        see enums.py

    """
    return_code = subprocess.call(
        ["bash", "bash_scripts/run_tests.sh", project_name, test_file_name]
    )

    match return_code:
        case ExitCodes.SUCCESS.value:
            return (True,)
        case ExitCodes.MISSING_REQUIREMENTS.value:
            return (False, "requirements.txt does not exist")
        case ExitCodes.MISSING_TEST_FILE.value:
            return (False, "test file does not exist")
        case ExitCodes.VENV_CREATION_ERROR.value:
            return (False, "Could not create venv folder.")


def parse_junitxml_file(project_name: str) -> None:
    pass

if __name__ == "__main__":
    clone_or_pull_project("https://github.com/Rayanworkout/MinimalistWebServer")
    run_test_script("MinimalistWebServer", "tests.py")
