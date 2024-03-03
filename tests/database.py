import sqlite3
import unittest
import sys

sys.path.append("..")
from workers.database import DBWorker


class TestDBWorker(unittest.TestCase):
    def setUp(self):
        self.db_worker = DBWorker("tests.sqlite3")

    def test_insert_project_to_database(self):
        self.db_worker.insert_project_to_database(
            "Project 1", "test_file_1.py", "github_url_1"
        )

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
            self.db_worker.insert_project_to_database(
                "Project 1", "test_file_1.py", "github_url_1"
            )

    def test_insert_project_custom_branch(self):
        self.db_worker.insert_project_to_database(
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
        self.db_worker.insert_project_to_database(
            "Project 3", "test_file_3.py", "github_url_3"
        )

        self.db_worker.insert_project_to_database(
            "Project 3", "test_file_3.py", "github_url_3"
        )

        project = self.db_worker.get_project("project 3")

        self.assertIsNotNone(project)

        self.assertEqual(len(project), 5)

    def test_get_all_projects(self):
        for x in range(200):
            self.db_worker.delete_project_by_id(x)

        self.db_worker.insert_project_to_database(
            "Project 4", "test_file_4.py", "github_url_4"
        )

        self.db_worker.insert_project_to_database(
            "Project 5", "test_file_5.py", "github_url_5"
        )

        all_projects = self.db_worker.get_all_projects()

        self.assertIsNotNone(all_projects)
        self.assertEqual(len(all_projects), 2)

    def test_insert_test_batch(self):
        self.db_worker.insert_project_to_database(
            "Project 4", "test_file_4.py", "github_url_4"
        )

        project = self.db_worker.get_project("project 4")

        batch = {
            "errors": 0,
            "failures": 0,
            "skipped": 0,
            "total": 0,
            "execution_time": 0.0,
            "timestamp": "2024-03-03T15:34:37.859003",
        }

        self.db_worker.insert_test_batch(project[0], batch)  # id of the project

        # Get all batches related to the project
        all_test_batch = self.db_worker.get_project_test_batches(project[0])

        self.assertIsNotNone(all_test_batch)
        self.assertEqual(
            len(all_test_batch[0]), 7
        )  # id, project_id, errors, failures, skipped, total, execution_time, datetime

    def test_add_test_case_to_a_batch(self):

        self.db_worker.insert_project_to_database(
            "Project 8", "test_file_8.py", "github_url_8"
        )

        project_instance = self.db_worker.get_project("project 8")

        batch = {
            "errors": 0,
            "failures": 0,
            "skipped": 0,
            "total": 0,
            "time": 0.0,
            "timestamp": "2024-03-03T15:34:37.859003",
        }

        self.db_worker.insert_test_batch(project_instance[0], batch)

        test_batches = self.db_worker.get_project_test_batches(project_instance[0])

        self.assertIsNotNone(test_batches)
        self.assertEqual(len(test_batches[0]), 7)

        self.db_worker.insert_many_test_cases(
            test_batches[0]["id"], [("testcase_1", 0.2)]
        )

        testcases = self.db_worker.get_test_cases_of_batch(test_batches[0]["id"])

        self.assertIsNotNone(testcases[0])
        self.assertEqual(len(testcases[0]), 4)  # id, batch_id, name, execution_time
        self.assertEqual(testcases[0][2], "testcase_1")

    def test_get_test_cases_of_a_batch(self):
        self.db_worker.insert_project_to_database(
            "Project 9", "test_file_9.py", "github_url_9"
        )

        project_instance = self.db_worker.get_project("project 9")

        batch = {
            "errors": 0,
            "failures": 0,
            "skipped": 0,
            "tests": 0,
            "time": 0.0,
            "timestamp": "2024-03-03T15:34:37.859003",
        }

        self.db_worker.insert_test_batch(project_instance[0], batch)

        test_batches = self.db_worker.get_project_test_batches(project_instance[0])

        self.assertIsNotNone(test_batches)
        self.assertEqual(len(test_batches[0]), 7)

        self.db_worker.insert_many_test_cases(
            test_batches[0]["id"], [("testcase_1", 0.2), ("testcase_2", 0.3)]
        )

        testcases = self.db_worker.get_test_cases_of_batch(test_batches[0]["id"])

        self.assertIsNotNone(testcases)
        self.assertEqual(len(testcases), 2)
        self.assertEqual(testcases[0][2], "testcase_1")
        self.assertEqual(testcases[1][2], "testcase_2")

    def test_get_all_projects_stats_empty_batches(self):

        # Delete all projects
        for x in range(200):
            self.db_worker.delete_project_by_id(x)
            self.db_worker.delete_test_batch_by_id(x)

        project_stats = self.db_worker.get_tests_statistics()

        self.assertIsNotNone(project_stats)
        self.assertEqual(project_stats["total"], 0)
        self.assertEqual(project_stats["success_rate"], 0)
        self.assertEqual(project_stats["failures"], 0)

    def test_all_projects_stats_with_batches(self):

        # Delete all projects
        for x in range(200):
            self.db_worker.delete_project_by_id(x)
            self.db_worker.delete_test_batch_by_id(x)

        # Insert 2 projects
        self.db_worker.insert_project_to_database(
            "Project 10", "test_file_10.py", "github_url_10"
        )

        self.db_worker.insert_project_to_database(
            "Project 11", "test_file_11.py", "github_url_11"
        )

        all_projects = self.db_worker.get_all_projects()

        all_projects_id = [project["id"] for project in all_projects]

        batch_1 = {
            "errors": 0,
            "failures": 5,
            "skipped": 0,
            "tests": 10,
            "time": 0.0,
            "timestamp": "2024-03-03T15:34:37.859003",
        }

        batch_2 = {
            "errors": 5,
            "failures": 0,
            "skipped": 0,
            "tests": 10,
            "time": 0.0,
            "timestamp": "2024-03-03T15:34:37.859003",
        }

        self.db_worker.insert_test_batch(all_projects_id[0], batch_1)
        self.db_worker.insert_test_batch(all_projects_id[1], batch_2)

        stats = self.db_worker.get_tests_statistics()

        self.assertIsNotNone(stats)
        self.assertEqual(stats["total"], 20)
        self.assertEqual(stats["success_rate"], 50)
        self.assertEqual(stats["failures"], 5)

    def test_statistic_of_one_project(self):
        # Delete all projects and batches
        for x in range(200):
            self.db_worker.delete_project_by_id(x)
            self.db_worker.delete_test_batch_by_id(x)

        self.db_worker.insert_project_to_database(
            "Project 12", "test_file_12.py", "github_url_12"
        )

        project = self.db_worker.get_project("project 12")

        batch_1 = {
            "errors": 0,
            "failures": 5,
            "skipped": 0,
            "tests": 10,
            "time": 0.0,
            "timestamp": "2024-03-03T15:34:37.859003",
        }

        batch_2 = {
            "errors": 5,
            "failures": 0,
            "skipped": 0,
            "tests": 10,
            "time": 0.0,
            "timestamp": "2024-03-03T15:34:37.859003",
        }

        self.db_worker.insert_test_batch(project[0], batch_1)
        self.db_worker.insert_test_batch(project[0], batch_2)

        stats = self.db_worker.get_project_statistics(project[0])

        self.assertIsNotNone(stats)
        self.assertEqual(stats["total"], 20)
        self.assertEqual(stats["success_rate"], 50)
        self.assertEqual(stats["failures"], 5)

if __name__ == "__main__":
    unittest.main()
