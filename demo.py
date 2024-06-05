import argparse
import os

from dotenv import load_dotenv

from flask import Flask, request, render_template, flash, redirect, url_for


from workers.database import DBWorker
from workers.project_manager import ProjectManager

# DEMO DATABSE NEEDED FOR THIS DEMO

app = Flask(__name__)

# Load the environment variables
load_dotenv()
app.secret_key = os.getenv("FLASK_SECRET_KEY")


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



@app.route("/add_project", methods=["GET", "POST"])
def add_project():
    """
    Flask route to add a new project to the database.

    Displays the form to add a new project and processes the form data.

    """

    if request.method == "POST":
        flash(f"Project can not be added on demo deployment.", "danger")

    return render_template("add_project.html")


@app.route("/delete_project/<string:project_name>", methods=["GET"])
def delete_project(project_name):
    """
    Flask route to delete a project folder and from the database.

    """

    flash("Project can not be deleted on demo deployment.", "danger")
    return redirect(url_for("index"))



@app.route("/about", methods=["GET"])
def about():
    return render_template("about.html")



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
