import logging

from flask import Flask, request, render_template

# Function to verify the signature
# To ensure that the payload was sent from GitHub
from workers.webhook_validator import WebhookValidator

app = Flask(__name__)

# Configure Flask logging
app.logger.setLevel(logging.INFO)  # Set log level to INFO
handler = logging.FileHandler("flask-app.log")  # Log to a file
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
app.logger.addHandler(handler)

projects = {
    "project1": {
        "test_file": "test_project1.py",
        "project_url": "",
        "target_branch": "main",
        "status": "idle",
    }
}

TARGET_BRANCH = "main"


@app.route("/")
def index():
    app.logger.info("Index page visited")
    return render_template("index.html")


@app.route("/test", methods=["POST"])
def test():
    """
    Flask route to trigger the test process

    """

    json_body = request.json
    branch = json_body["ref"].split("/")[-1]

    if branch != TARGET_BRANCH:
        return {"status": "success", "message": "not target branch"}

    secret_header = request.headers.get("X-Hub-Signature-256")
    payload = request.data

    if WebhookValidator.verify_signature(
        payload_body=payload,
        signature_header=secret_header,
    ):

        # Call the test script

        return {"status": "success", "message": "test process triggered"}

    else:
        return {"status": "error", "message": "Invalid signature"}


# @app.errorhandler(500)
# def server_error(error):
#     app.logger.exception('An exception occurred during a request.')
#     return 'Internal Server Error', 500


app.run()
