import sqlite3
from datetime import datetime


class DBWorker:
    """
    Worker object for the database.

    Contains methods to insert and retrieve data from the database.
    Each project is saved into the projects table with necessary information.

    The test cases are saved into the test_cases table.
    Each test case is associates with a batch of tests, which is saved into the test_batches table.

    Each batch of test cases is associated with a project.

    A one to many relationship is established between projects and test_batches.
    A one to many relationship is established between test_batches and test_cases.

    A project can have many test batches.
    A test batch can have many test cases.

    A test case can only belong to one test batch.
    A test batch can only belong to one project.

    """

    __instance = None

    # Enforcing usage of a singleton
    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self, db_file: str = "data.sqlite3"):
        self.__conn = sqlite3.connect(db_file)
        self.__cursor = self.__conn.cursor()

        # Project table
        self.__cursor.execute(
            """CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE,
                    test_file TEXT,
                    github_url TEXT,
                    target_branch TEXT
                )"""
        )

        # Batch table
        self.__cursor.execute(
            """CREATE TABLE IF NOT EXISTS test_batches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER,
                    errors INTEGER DEFAULT 0,
                    failures INTEGER DEFAULT 0,
                    skipped INTEGER DEFAULT 0,
                    total INTEGER DEFAULT 0,
                    execution_time REAL DEFAULT 0,
                    datetime TEXT,
                    FOREIGN KEY (project_id) REFERENCES projects(id)
                )"""
        )

        # Test case table
        self.__cursor.execute(
            """CREATE TABLE IF NOT EXISTS test_cases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    test_batch_id INTEGER,
                    test_name TEXT,
                    duration REAL,
                    FOREIGN KEY (test_batch_id) REFERENCES test_batches(id)
                )"""
        )
        self.__conn.commit()

    ####### PROJECTS #######
    def insert_project_to_database(
        self, name: str, test_file: str, github_url: str, target_branch: str = "main"
    ) -> bool:
        """
        Insert a new project into the database.

        Params:
            name: name of the project
            test_file: the file that contains the tests to be run
            github_url: github url of the project
            target_branch: the branch that should trigger the tests, default is main

        Returns:
            True if the project was inserted successfully
            False otherwise

        """
        success = self.__cursor.execute(
            """INSERT OR IGNORE INTO projects (name, test_file, github_url, target_branch)
                VALUES (?, ?, ?, ?)""",
            (name.lower(), test_file, github_url, target_branch),
        )
        self.__conn.commit()

        return success.rowcount > 0

    def get_project(self, name: str) -> tuple:
        """
        Get a project from the database.

        Params:
            name: name of the project

        Returns:
            A tuple with the project data

        """
        self.__cursor.execute("""SELECT * FROM projects WHERE name = ?""", (name,))

        return self.__cursor.fetchone()

    def get_project_target_branch(self, name: str) -> str:
        """
        Get the target branch of a project from the database.

        Params:
            name: name of the project

        Returns:
            The target branch of the project

        """
        self.__cursor.execute(
            """SELECT target_branch FROM projects WHERE name = ?""", (name,)
        )

        return self.__cursor.fetchone()[0]

    def get_all_projects(self) -> list[dict]:
        """
        Get all the projects from the database.

        Returns:
            A list of dicts with all projects, and for each project:
                - id
                - name
                - test_file
                - github_url
                - target_branch
                - last_batch
        """
        projects = []
        data = self.__cursor.execute("""SELECT * FROM projects""")

        for project in data.fetchall():
            id_, name, test_file, github_url, target_branch = project

            last_batch = self.get_project_test_batches(id_)[0]

            projects.append(
                {
                    "id": id_,
                    "name": name.capitalize(),
                    "test_file": test_file,
                    "github_url": github_url.replace("https://github.com/", ""),
                    "target_branch": target_branch,
                    "last_batch": last_batch["datetime"],
                }
            )

        return projects

    def get_project_by_id(self, project_id: int) -> dict:
        """
        Get a project from the database by its id.

        Params:
            project_id: the id of the project

        Returns:
            A dict with the project data

        """
        self.__cursor.execute("""SELECT * FROM projects WHERE id = ?""", (project_id,))

        _, name, test_file, github_url, target_branch = self.__cursor.fetchone()

        project = {
            "id": project_id,
            "name": name.capitalize(),
            "test_file": test_file,
            "github_url": github_url,
            "target_branch": target_branch,
        }

        return project

    def delete_project_by_id(self, project_id: str) -> None:
        """
        Delete a project from the database by its id.

        Params:
            name: the name of the project

        """
        self.__cursor.execute("""DELETE FROM projects WHERE id = ?""", (project_id,))
        self.__conn.commit()

    def delete_project_by_name(self, name: str) -> bool:
        """
        Delete a project from the database by its name.

        Params:
            name: the name of the project

        Returns:
            True if the project was deleted successfully
            False otherwise

        """
        name = name.lower()
        success = self.__cursor.execute(
            """DELETE FROM projects WHERE name = ?""", (name,)
        )
        self.__conn.commit()

        return success.rowcount > 0

    def project_exists(self, name: str) -> bool:
        """
        Check if a project exists in the database.

        Params:
            name: the name of the project

        Returns:
            True if the project exists
            False otherwise

        """
        self.__cursor.execute("""SELECT * FROM projects WHERE name = ?""", (name,))
        return self.__cursor.fetchone() is not None

    ####### BATCHES #######
    def insert_test_batch(self, project_id: int, batch: tuple) -> int:
        """
        Insert a test batch into the database.

        Params:
            project_id: the id of the project
            batch: a tuple with the batch data (errors, failures, skipped, total, execution_time, datetime)

        Returns:
            The id of the last inserted row to be able to insert test cases to
            this batch.

        """

        errors, failures = batch.get("errors", 0), batch.get("failures", 0)
        skipped, total = batch.get("skipped", 0), batch.get("tests", 0)
        execution_time = batch.get("time", 0)
        timestamp = batch.get("timestamp", None)

        self.__cursor.execute(
            """INSERT OR IGNORE INTO test_batches (project_id, errors, failures, skipped, total, execution_time, datetime) VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (project_id, errors, failures, skipped, total, execution_time, timestamp),
        )
        self.__conn.commit()

        # Retrieve the ID of the last inserted row
        batch_id = self.__cursor.lastrowid
        return batch_id

    def get_project_test_batches(self, project_id: int) -> dict:
        """
        Get all the test batches for a specified project.

        Params:
            project_id: the id of the project

        Returns:
            A dict with the test batch data for the specified project, sorted by datetime.

        """

        batches = []
        self.__cursor.execute(
            """SELECT * FROM test_batches WHERE project_id = ?""",
            (project_id,),
        )

        for batch in self.__cursor.fetchall():
            # Unpack the batch data
            (
                id_,
                _,
                errors,
                failures,
                skipped,
                total,
                execution_time,
                batch_datetime,
            ) = batch

            datetime_obj = datetime.strptime(batch_datetime, "%Y-%m-%dT%H:%M:%S.%f")

            batches.append(
                {
                    "id": id_,
                    "errors": errors,
                    "failures": failures,
                    "skipped": skipped,
                    "total": total,
                    "execution_time": str(execution_time) + " s",
                    "datetime": datetime_obj.strftime("%Y-%m-%d | %H:%M"),
                }
            )

        # Sort the batches by datetime
        batches = sorted(batches, key=lambda x: x["datetime"], reverse=True)

        return batches if batches else [{"datetime": "No tests yet."}]

    def delete_test_batch_by_id(self, batch_id: int) -> None:
        """
        Delete a test batch from the database by its id.

        Params:
            batch_id: the id of the project

        """
        self.__cursor.execute("""DELETE FROM test_batches WHERE id = ?""", (batch_id,))
        self.__conn.commit()

    ####### TEST CASES #######
    def insert_many_test_cases(
        self, test_batch_id: int, test_cases: list[(str, float)]
    ) -> None:
        """
        Insert multiple test cases to a batch of tests.

        Params:
            project_id: the id of the project
            test_name: the name of the test
            duration: the duration of the test

        """
        for test_name, duration in test_cases:
            self.__cursor.execute(
                """INSERT INTO test_cases (test_batch_id, test_name, duration)
                    VALUES (?, ?, ?)""",
                (test_batch_id, test_name, duration),
            )
        self.__conn.commit()

    def get_test_cases_of_batch(self, test_batch_id: int) -> tuple:
        """
        Get all the test cases for a specified test batch.

        Params:
            test_batch_id: the id of the test batch

        Returns:
            A tuple with the test case data

        """
        self.__cursor.execute(
            """SELECT * FROM test_cases WHERE test_batch_id = ?""",
            (test_batch_id,),
        )
        return self.__cursor.fetchall()

    ####### STATISTICS #######
    def get_tests_statistics(self) -> dict:
        """
        Get statitics about all the tests.

        Returns a dict with:
            - total: the total number of tests
            - success_rate: the success rate of the tests
            - failures: the number of failed tests

        """
        total_tests_sum = self.__cursor.execute(
            """SELECT SUM(total) FROM test_batches"""
        ).fetchone()[0]

        # Cast to real to have float division
        total_tests_success_rate = self.__cursor.execute(
            """SELECT (CAST(SUM(total - errors - failures - skipped) AS REAL) / SUM(total)) * 100 FROM test_batches"""
        ).fetchone()[0]

        total_tests_failures = self.__cursor.execute(
            """SELECT SUM(failures) FROM test_batches"""
        ).fetchone()[0]

        if total_tests_sum is None:  # If there are no tests at all
            total_tests_sum = 0
            total_tests_success_rate = 0
            total_tests_failures = 0

        stats = {
            "total": total_tests_sum,
            "success_rate": round(total_tests_success_rate, 2),
            "failures": total_tests_failures,
        }

        return stats

    def get_project_statistics(self, project_id: int) -> dict:
        """
        Get statistics about a specific project.

        Params:
            project_id: the id of the project

        Returns a dict with:
            - total: the total number of tests
            - success_rate: the success rate of the tests
            - failures: the number of failed tests

        """
        total_tests_sum = self.__cursor.execute(
            """SELECT SUM(total) FROM test_batches WHERE project_id = ?""",
            (project_id,),
        ).fetchone()[0]

        total_tests_success_rate = self.__cursor.execute(
            """SELECT (CAST(SUM(total - errors - failures - skipped) AS REAL) / SUM(total)) * 100 FROM test_batches WHERE project_id = ?""",
            (project_id,),
        ).fetchone()[0]

        total_tests_failures = self.__cursor.execute(
            """SELECT SUM(failures) FROM test_batches WHERE project_id = ?""",
            (project_id,),
        ).fetchone()[0]

        if total_tests_sum is None:  # If there are no tests for this project
            total_tests_sum = 0
            total_tests_success_rate = 0
            total_tests_failures = 0

        stats = {
            "total": total_tests_sum,
            "success_rate": round(total_tests_success_rate, 2),
            "failures": total_tests_failures,
        }

        return stats

    def close(self) -> None:
        """
        Close the connection to the database.

        """
        self.__conn.close()
