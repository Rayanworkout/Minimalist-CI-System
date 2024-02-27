import os
import subprocess


def run_script_in_venv(venv_path: str, tests_script_path: str, system: str) -> None:
    """
    Run the tests python script in a virtual environment. We define commands
    according to the operating system.

    Arguments:
        - venv_path: str: The path to the folder CONTAINING the virtual environment.
        - tests_script_path: str: The path to the tests script.
        - system: str: The operating system. Either "nt" or "posix".

    TODO: Catch exceptions and log them.

    """
    # Activate the virtual environment
    if system == "nt":
        activate_script = os.path.join(venv_path, "Scripts", "activate.bat")
        activation_command = f"call {activate_script}"
        command = f"python {tests_script_path}"

    elif system == "posix":
        activate_script = os.path.join(venv_path, "bin", "activate")
        command = f"source {activate_script} && python3 {tests_script_path}"

    else:
        raise ValueError("Unsupported operating system")

    subprocess.run(command, shell=True, check=True)

    # Execute the command in a subprocess
    # subprocess.run(command, shell=True, check=True)


PROJECT_FOLDER = "/home/rayan/dev/projects_backup/MinimalistWebServer"
TESTS_FILE = "tests.py"

VENV = True
if VENV:
    VENV_NAME = ".venv"
    VENV_FULL_PATH = os.path.join(PROJECT_FOLDER, VENV_NAME)
    
    

    run_script_in_venv(VENV_FULL_PATH, TESTS_FILE, os.name)
