import argparse
import logging
import os

from dotenv import load_dotenv

from flask import Flask, request, render_template, flash, redirect, url_for

# Function to verify the signature
# To ensure that the payload was sent from GitHub
from workers.webhook_validator import WebhookValidator

from workers.database import DBWorker
from workers.project_manager import ProjectManager
from workers.tester import Tester

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


# TODO handle target branch according to database
# Handle test file in folder
# Handle project name from github delivery
# Handle private repositories
# Check if a project in database also exists as a folder at every start
# Get repo name from url and not user input
# Enable user to delete project (ProjectManager.delete_project)
# Monitor when project is not cloned (bad url)
# Monitor if a project is well deleted (projectManager.delete_project and database.delete_project_by_name)


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

    print(json_body)

    if branch != TARGET_BRANCH:
        return {"status": "success", "message": "not target branch"}

    secret_header = request.headers.get("X-Hub-Signature-256")
    payload = request.data

    if WebhookValidator.verify_signature(
        payload_body=payload,
        signature_header=secret_header,
    ):

        ProjectManager.pull_latest_changes()
        Tester.perform_tests()

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

        name = name.lower()  # Project name is lowercase inside the database

        # Project does not exist in DB
        if not db_worker.project_exists(name):
            # project hasn't been cloned yet
            if not ProjectManager.project_exists(github_url):
                ProjectManager.clone_project(github_url)

            db_worker.insert_project_to_database(
                name, test_file, github_url, target_branch
            )

            # If form submission is successful, display a success message
            flash("Project added successfully.", "success")

            app.logger.info(f"new project added: {name}")
            # And redirect to the index
            return redirect(url_for("index"))
        else:
            flash("Project already exists.", "danger")
            app.logger.info(f"project already exists: {name}")
            return redirect(url_for("add_project"))

    return render_template("add_project.html")


@app.route("/delete_project/<string:project_name>", methods=["GET"])
def delete_project(project_name):
    """
    Flask route to delete a project folder and from the database.

    """

    db_worker = DBWorker()
    db_worker.delete_project_by_name(project_name)

    ProjectManager.delete_project_folder(project_name)

    app.logger.info(f"project deleted: {project_name}")

    flash("Project deleted successfully.", "success")
    return redirect(url_for("index"))


@app.route("/about", methods=["GET"])
def about():
    return render_template("about.html")


# @app.errorhandler(500)
# def server_error(error):
#     app.logger.exception('An exception occurred during a request.')
#     return 'Internal Server Error', 500


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Simple Continuous Integration Server")
    # Port
    parser.add_argument(
        "--port", type=int, default=8080, help="Port number for the server"
    )

    # Host
    parser.add_argument(
        "--host", type=str, default="127.0.0.1", help="Host address for the server"
    )

    args = parser.parse_args()

    app.run(debug=True, threaded=True, host=args.host, port=args.port)
