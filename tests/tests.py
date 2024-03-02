import unittest
import sqlite3
import sys

sys.path.append("..")
from workers.database import DBWorker


class TestDBWorker(unittest.TestCase):
    def setUp(self):
        self.db_worker = DBWorker()
        self.conn = sqlite3.connect("tests.sqlite3")
        self.cursor = self.conn.cursor()

    def tearDown(self):
        self.cursor.execute("DELETE FROM projects")
        self.cursor.execute("DELETE FROM test_batches")
        self.cursor.execute("DELETE FROM test_cases")
        self.conn.commit()
        self.conn.close()

    def test_insert_project(self):
        self.db_worker.insert_project("Project 1", "test_file_1.py", "github_url_1")
        project = self.db_worker.get_project("Project 1")
        self.assertIsNotNone(project)
        self.assertEqual(project[1], "Project 1")
        self.assertEqual(project[2], "test_file_1.py")
        self.assertEqual(project[3], "github_url_1")

    def test_insert_test_batch(self):
        self.db_worker.insert_project("Project 2", "test_file_2.py", "github_url_2")
        project = self.db_worker.get_project("Project 2")
        self.db_worker.insert_test_batch(project[0], "Batch 1")
        test_batch = self.db_worker.get_test_batches(project[0])
        self.assertIsNotNone(test_batch)
        self.assertEqual(test_batch[1], "Batch 1")

    def test_insert_test_case(self):
        self.db_worker.insert_project("Project 3", "test_file_3.py", "github_url_3")
        project = self.db_worker.get_project("Project 3")
        self.db_worker.insert_test_batch(project[0], "Batch 2")
        test_batch = self.db_worker.get_test_batches(project[0])
        self.db_worker.insert_test_case(project[0], "Test 1", "10s")
        test_cases = self.db_worker.get_test_cases(test_batch[0])
        self.assertIsNotNone(test_cases)
        self.assertEqual(test_cases[2], "Test 1")


if __name__ == "__main__":
    unittest.main()
