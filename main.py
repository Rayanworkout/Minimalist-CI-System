import logging

from flask import Flask, request, render_template

# Function to verify the signature
# To ensure that the payload was sent from GitHub
from validate_hash import verify_signature
from perform_tests import run_tests

app = Flask(__name__)

# Configure Flask logging
app.logger.setLevel(logging.INFO)  # Set log level to INFO
handler = logging.FileHandler("flask-app.log")  # Log to a file
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
app.logger.addHandler(handler)

# 1 fonctionnalité par classe, découpage par services selon responsabilités


TARGET_BRANCH = "main"


@app.route("/")
def index():
    app.logger.info("Index page visited")
    run_tests()
    return render_template("index.html")


@app.route("/build", methods=["POST"])
def build():
    """
    Flask route to trigger the build process

    """

    json_body = request.json
    branch = json_body["ref"].split("/")[-1]

    if branch != TARGET_BRANCH:
        return {"status": "success", "message": "Not target branch"}

    secret_header = request.headers.get("X-Hub-Signature-256")
    payload = request.data

    if verify_signature(
        payload_body=payload,
        signature_header=secret_header,
    ):

        # Call the test script

        return {"status": "success", "message": "Test process triggered"}

    else:
        return {"status": "error", "message": "Invalid signature"}


# @app.errorhandler(500)
# def server_error(error):
#     app.logger.exception('An exception occurred during a request.')
#     return 'Internal Server Error', 500


app.run()
