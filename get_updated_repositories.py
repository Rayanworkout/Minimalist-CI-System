import os
import subprocess


def get_repo(repository_name: str, branch: str):
    """
    Clone the repository and checkout the specified branch.

    Arguments:
        - repository_name: str: The name of the repository.
        - branch: str: The branch to checkout.
        - commit_sha: str: The commit SHA to checkout.

    Returns:
        - None

    """
    current_dir = os.path.dirname(__file__)
    projects_folder = os.path.join(current_dir, "projects")
    # Clone the repository
    if not os.path.exists(projects_folder):
        print(f"Creating {projects_folder}")
        os.makedirs(projects_folder)
    
    os.chdir(projects_folder)
    
    clone_command = f"git clone https://github.com/rayanworkout/{repository_name}.git"

    subprocess.run(clone_command, shell=True)


get_repo("MinimalistWebServer", "main")
