import unittest
import sys

sys.path.append("../")

from workers.webhook_validator import WebhookValidator


class TestTesterWorker(unittest.TestCase):
    def setUp(self):
        pass

    def test_verify_signature(self):
        
        signature_header = "sha256=757107ea0eb2509fc211221cce984b8a37570b6d7586c22c46f4379c8b043e17"
        payload = "Hello, World!"

        self.assertTrue(
            WebhookValidator.verify_signature(
                payload_body=payload.encode(), signature_header=signature_header
            )
        )


if __name__ == "__main__":
    unittest.main()
