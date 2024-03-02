import sqlite3
import unittest
import sys

sys.path.append("..")
from workers.database import DBWorker


class TestDBWorker(unittest.TestCase):
    def setUp(self):
        self.db_worker = DBWorker("tests.sqlite3")

    def test_insert_project(self):
        self.db_worker.insert_project("Project 1", "test_file_1.py", "github_url_1")

        project = self.db_worker.get_project("project 1")

        self.assertIsNotNone(project)
        _, name, test_file, github_url, target_branch = project
        self.assertEqual(name, "project 1")
        self.assertEqual(test_file, "test_file_1.py")
        self.assertEqual(github_url, "github_url_1")
        self.assertEqual(target_branch, "main")

    def test_close_method_works(self):
        self.db_worker.close()

        with self.assertRaises(sqlite3.ProgrammingError):
            self.db_worker.insert_project("Project 1", "test_file_1.py", "github_url_1")

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

    def test_insert_test_batch(self):
        self.db_worker.insert_project("Project 4", "test_file_4.py", "github_url_4")

        project = self.db_worker.get_project("project 4")

        self.db_worker.insert_test_batch(project[0])  # id of the project

        test_batches = self.db_worker.get_test_batches(project[0])

        self.assertIsNotNone(test_batches)
        self.assertEqual(len(test_batches), 4)  # id, name and project_id

    # def test_insert_batch_with_custom_name(self):

    #     project = self.db_worker.get_project_by_id(1)

    #     self.db_worker.insert_test_batch(project[0], "custom_name")

    #     test_batch = self.db_worker.get_test_batches(project[0])

    #     self.assertIsNotNone(test_batch)
    #     self.assertEqual(len(test_batch), 4)
    #     self.assertEqual(test_batch[1], "custom_name")

    def test_add_testcase_to_a_batch(self):

        project = self.db_worker.insert_project(
            "Project 8", "test_file_8.py", "github_url_8"
        )

        project_instance = self.db_worker.get_project("project 8")

        self.db_worker.insert_test_batch(project_instance[0], "test_batch")

        test_batch = self.db_worker.get_test_batches(project_instance[0])

        self.assertIsNotNone(test_batch)
        self.assertEqual(len(test_batch), 4)
        self.assertEqual(test_batch[1], "test_batch")

        self.db_worker.insert_test_case(test_batch[0], "testcase_1", 0.2)

        # testcases = self.db_worker.get_testcases(test_batch[0])

        # self.assertIsNotNone(testcases)
        # self.assertEqual(len(testcases), 3)
        # self.assertEqual(testcases[1], "testcase_1")


if __name__ == "__main__":
    unittest.main()
