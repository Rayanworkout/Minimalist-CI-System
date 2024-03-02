import sqlite3


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

    def insert_project(
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
        self.__cursor.execute(
            """INSERT OR IGNORE INTO projects (name, test_file, github_url, target_branch)
                VALUES (?, ?, ?, ?)""",
            (name.lower(), test_file, github_url, target_branch),
        )
        self.__conn.commit()

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

    def get_project_by_id(self, project_id: int) -> tuple:
        """
        Get a project from the database by its id.

        Params:
            project_id: the id of the project

        Returns:
            A tuple with the project data

        """
        self.__cursor.execute("""SELECT * FROM projects WHERE id = ?""", (project_id,))
        return self.__cursor.fetchone()

    def insert_test_batch(self, project_id: int, batch: tuple) -> None:
        """
        Insert a test batch into the database.

        Params:
            project_id: the id of the project
            batch: a tuple with the batch data (errors, failures, skipped, total, execution_time, datetime)

        """

        errors, failures = batch.get("errors", 0), batch.get("failures", 0)
        skipped, total = batch.get("skipped", 0), batch.get("total", 0)
        execution_time = batch.get("time", 0)
        timestamp = batch.get("timestamp", None)

        self.__cursor.execute(
            """INSERT OR IGNORE INTO test_batches (project_id, errors, failures, skipped, total, execution_time, datetime) VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (project_id, errors, failures, skipped, total, execution_time, timestamp),
        )
        self.__conn.commit()

    def get_test_batches(self, project_id: int) -> tuple:
        """
        Get all the test batches for a specified project.

        Params:
            project_id: the id of the project

        Returns:
            A tuple with the test batch data

        """
        self.__cursor.execute(
            """SELECT * FROM test_batches WHERE project_id = ?""",
            (project_id,),
        )
        return self.__cursor.fetchall()

    def insert_test_case(
        self, test_batch_id: int, test_name: str, duration: float
    ) -> None:
        """
        Insert a test case into the database.

        Params:
            project_id: the id of the project
            test_name: the name of the test
            duration: the duration of the test

        """
        self.__cursor.execute(
            """INSERT INTO test_cases (test_batch_id, test_name, duration)
                VALUES (?, ?, ?)""",
            (test_batch_id, test_name, duration),
        )
        self.__conn.commit()

    def get_test_cases(self, test_batch_id: int) -> tuple:
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

    def close(self) -> None:
        """
        Close the connection to the database.

        """
        self.__conn.close()
