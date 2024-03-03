import unittest
import sys

sys.path.append("../")

from workers.tester import Tester


class TestTesterWorker(unittest.TestCase):
    def setUp(self):
        pass

    # def test_class_attributes(self):
    #     self.assertEqual(Tester.__test_script_path, "../bash_scripts/run_tests.sh")
    #     self.assertEqual(Tester.__db_worker, None)


if __name__ == "__main__":
    unittest.main()
