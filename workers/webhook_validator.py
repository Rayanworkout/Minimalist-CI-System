import hashlib
import hmac
import os

from dotenv import load_dotenv


class WebhookValidator:
    """
    Validates incoming webhooks from GitHub.

    """

    @classmethod
    def verify_signature(cls, payload_body: bytes, signature_header: str) -> bool:
        """Verify that the payload was sent from GitHub by validating SHA256.

        https://docs.github.com/en/webhooks/webhook-events-and-payloads

        Returns:
            False if the signature is invalid or missing
            True if the signature is valid

        Args:
            payload_body: original request body to verify as bytes
            signature_header: header received from GitHub (x-hub-signature-256)
        """

        load_dotenv()

        # GitHub app webhook token (WEBHOOK_SECRET)
        secret_key = os.getenv("GITHUB_WEBHOOK_SECRET")
        # secret_key = "It's a Secret to Everybody"  # Test purposes

        # No further processing if signature is missing or not retrieved
        if secret_key is None or signature_header is None:
            return False

        # We encode the secret token and the payload body
        hash_object = hmac.new(
            secret_key.encode("utf-8"), msg=payload_body, digestmod=hashlib.sha256
        )

        # We compare the expected signature with the received signature
        expected_signature = "sha256=" + hash_object.hexdigest()

        # We use the compare_digest method to prevent timing attacks
        if hmac.compare_digest(expected_signature, signature_header):
            return True

        return False
