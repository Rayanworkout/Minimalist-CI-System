import os
import unittest
import sys

sys.path.append("..")
from workers.database import DBWorker


class TestDBWorker(unittest.TestCase):
    def setUp(self):
        self.db_worker = DBWorker("tests.sqlite3")

    def tearDown(self):
        self.db_worker.close()

    def test_insert_project(self):
        self.db_worker.insert_project("Project 1", "test_file_1.py", "github_url_1")

        project = self.db_worker.get_project("project 1")

        self.assertIsNotNone(project)
        _, name, test_file, github_url, target_branch = project
        self.assertEqual(name, "project 1")
        self.assertEqual(test_file, "test_file_1.py")
        self.assertEqual(github_url, "github_url_1")
        self.assertEqual(target_branch, "main")

    def test_insert_project_custom_branch(self):
        self.db_worker.insert_project(
            "Project 2", "test_file_2.py", "github_url_2", "develop"
        )

        project = self.db_worker.get_project("project 2")

        self.assertIsNotNone(project)
        _, name, test_file, github_url, target_branch = project
        self.assertEqual(name, "project 2")
        self.assertEqual(test_file, "test_file_2.py")
        self.assertEqual(github_url, "github_url_2")
        self.assertEqual(target_branch, "develop")

    def test_insert_project_duplicate(self):
        self.db_worker.insert_project("Project 3", "test_file_3.py", "github_url_3")

        self.db_worker.insert_project("Project 3", "test_file_3.py", "github_url_3")

        project = self.db_worker.get_project("project 3")

        self.assertIsNotNone(project)

        self.assertEqual(len(project), 5)


if __name__ == "__main__":
    unittest.main()
