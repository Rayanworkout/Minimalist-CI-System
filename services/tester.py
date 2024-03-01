import os
import subprocess

from enums import ExitCodes


class Tester:
    """
    Run tests and parse results.
    """

    # Get the path of the current Python script
    __current_dir = os.path.dirname(os.path.abspath(__file__))
    __parent_dir = os.path.dirname(__current_dir)

    # Path to the bash_scripts directory
    __bash_scripts_dir = os.path.join(__parent_dir, "bash_scripts")

    __test_script_path = os.path.join(__bash_scripts_dir, "run_tests.sh")

    @classmethod
    def run_test_script(
        cls, project_name: str, test_file_name: str
    ) -> tuple[(ExitCodes, str)]:
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

    @staticmethod
    def get_junitxml_file(project_name: str) -> str:
        project_folder = os.join()
        xml_files = [file for file in os.listdir(project_folder) if file.endswith(".xml")]

    @classmethod
    def parse_junitxml_file(cls, project_name: str) -> None:
        pass
