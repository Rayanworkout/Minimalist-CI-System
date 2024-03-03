import os
import subprocess

from workers.enums import ExitCodes


class ProjectManager:
    """
    Clone, pull and manage projects files.
    """

    # Get the path of the current Python script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)

    # Path to the bash_scripts directory
    bash_scripts_dir = os.path.join(parent_dir, "bash_scripts")

    clone_script_path = os.path.join(bash_scripts_dir, "clone_project.sh")
    pull_script_path = os.path.join(bash_scripts_dir, "pull_latest_changes.sh")

    @classmethod
    def clone_project(cls, project_url: str) -> bool:
        """Clone a project inside projects/ folder.

        Params:
            project_url: github project url as string, like this: https://github.com/username/project

        The function calls a bash script to perform the operation, with 2 args: project url and project name.

        Returns:
            True if script execution went well, otherwise False.

        """

        # Extract project name from URL, last index after last /
        project_name = project_url.split("/")[-1]

        return_code = subprocess.call(
            [
                "bash",
                cls.clone_script_path,
                project_name,
                project_url,
            ]
        )

        # Exit code 0 == success
        if return_code == ExitCodes.SUCCESS.value:
            return True
        else:
            return False

    @classmethod
    def pull_latest_changes(cls, project_name: str) -> bool:
        """
        Pull latest changes from a project.

        Params:
            project_name: name of the project

        Returns:
            True if script execution went well, otherwise False.

        """
        return_code = subprocess.call(["bash", cls.pull_script_path, project_name])

        # Exit code 0 == success
        if return_code == ExitCodes.SUCCESS.value:
            return True
        else:
            return False

    @classmethod
    def project_exists(cls, project_name: str) -> bool:
        """
        Check if a project exists.

        Params:
            project_name: name of the project

        Returns:
            True if project exists, otherwise False.

        """
        project_folder = os.path.join(cls.parent_dir, "projects", project_name)

        return os.path.exists(project_folder)
