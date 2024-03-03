import logging
import os

from dotenv import load_dotenv

from flask import Flask, request, render_template, flash, redirect, url_for

# Function to verify the signature
# To ensure that the payload was sent from GitHub
from workers.webhook_validator import WebhookValidator

from workers.database import DBWorker

app = Flask(__name__)

# Load the environment variables
load_dotenv()
app.secret_key = os.getenv("FLASK_SECRET_KEY")


# Configure Flask logging
app.logger.setLevel(logging.INFO)  # Set log level to INFO
handler = logging.FileHandler("flask-app.log")  # Log to a file
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
app.logger.addHandler(handler)

TARGET_BRANCH = "main"


@app.route("/")
def index():
    db_worker = DBWorker()
    statistics: dict = db_worker.get_tests_statistics()
    all_projects: list[dict] = db_worker.get_all_projects()

    return render_template("index.html", statistics=statistics, projects=all_projects)


@app.route("/project/<int:project_id>")
def project(project_id):
    """
    View that displays the project details and test statistics.

    """
    db_worker = DBWorker()
    project: dict = db_worker.get_project_by_id(project_id)
    project_stats: dict = db_worker.get_project_statistics(project_id)
    test_batches: dict = db_worker.get_project_test_batches(project_id)

    app.logger.info(f"accessed project: {project['name']}")

    return render_template(
        "project.html", project=project, test_batches=test_batches, stats=project_stats
    )


@app.route("/test", methods=["POST"])
def test():
    """
    Flask route to trigger the test process.

    """

    app.logger.info("Test process triggered")

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


@app.route("/add_project", methods=["GET", "POST"])
def add_project():
    """
    Flask route to add a new project to the database.

    Displays the form to add a new project and processes the form data.

    """

    if request.method == "POST":
        db_worker = DBWorker()

        name, test_file, github_url, target_branch = (
            request.form["name"],
            request.form["test_file"],
            request.form["github_url"],
            request.form["branch"],
        )
        db_worker.insert_project_to_database(name, test_file, github_url, target_branch)

        # If form submission is successful, display a success message
        flash("Project added successfully.", "success")

        app.logger.info(f"new project added: {name}")
        # And redirect to the index
        return redirect(url_for("index"))

    return render_template("add_project.html")


@app.route("/about", methods=["GET"])
def about():
    return render_template("about.html")


# @app.errorhandler(500)
# def server_error(error):
#     app.logger.exception('An exception occurred during a request.')
#     return 'Internal Server Error', 500


if __name__ == "__main__":
    app.run(debug=True)
