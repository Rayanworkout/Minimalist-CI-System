import os
import subprocess

from database import DBWorker
from project_manager import ProjectManager

from enums import ExitCodes

import xml.etree.ElementTree as ET


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

    __db_worker = DBWorker()

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
            ["bash", cls.__test_script_path, project_name, test_file_name]
        )
        
        match return_code:
            case ExitCodes.SUCCESS.value:
                return (True, "Success")
            case ExitCodes.ERROR_EXIT.value:
                return (True, "Success with some errors")
            case ExitCodes.MISSING_REQUIREMENTS.value:
                return (False, "requirements.txt does not exist")
            case ExitCodes.MISSING_TEST_FILE.value:
                return (False, "test file does not exist")
            case ExitCodes.VENV_CREATION_ERROR.value:
                return (False, "Could not create venv folder.")

    @classmethod
    def get_junitxml_file(cls, project_name: str) -> str:

        project_folder = os.path.join(cls.__parent_dir, "projects", project_name)

        xml_files = [
            file for file in os.listdir(project_folder) if file.endswith(".xml")
        ]
        # We take the first file in the list
        test_file = xml_files[0]

        test_file_path = os.path.join(project_folder, test_file)

        return test_file_path

    @classmethod
    def parse_junitxml_file(cls, project_name: str) -> None:

        # get_junitxml_file returns both the file name and the project folder path
        test_file_path = cls.get_junitxml_file(project_name)

        tree = ET.parse(test_file_path)
        root = tree.getroot()

        # Contains errors, failures, skipped, timestamp ...
        test_result = root[0].attrib

        # Extract the testcases
        testcases_elems = root[0].findall("testcase")
        testcases = (
            (elem.attrib["name"], elem.attrib["time"]) for elem in testcases_elems
        )

        return (project_name, test_result, testcases)

    @classmethod
    def perform_tests(cls, project_name: str) -> list[dict]:
        """
        Run tests for a specific projects.

        Insert the result to the database.

        """

        # Check if project exists in the database
        project = cls.__db_worker.get_project(
            project_name.lower()
        )  # project_name is lowercased in the database

        if project is None:
            return {
                "status": "error",
                "message": "project not found, please add it first",
            }

        project_id = project[0]
        test_file = project[2]

        # Run the test script
        success, message = cls.run_test_script(project_name, test_file)

        if success is False:
            return {"status": "error", "message": message}

        # Parse the junitxml file
        project_name, test_result, testcases = cls.parse_junitxml_file(project_name)

        batch_id = cls.__db_worker.insert_test_batch(project_id, test_result)

        cls.__db_worker.insert_many_test_cases(batch_id, list(testcases))


if __name__ == "__main__":
    DBWorker().insert_project_to_database(
        "MinimalistWebServer",
        "tests.py",
        "https://github.com/Rayanworkout/MinimalistWebServer" "main",
    )

    if ProjectManager.project_exists("MinimalistWebServer"):
        Tester.perform_tests("MinimalistWebServer")
    else:
        ProjectManager.clone_project(
            "https://github.com/Rayanworkout/MinimalistWebServer"
        )
        Tester.perform_tests("MinimalistWebServer")
