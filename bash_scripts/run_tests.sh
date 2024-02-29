#!/bin/bash

set -e # exit program if a command returns a non-zero status

project_name="$1"
test_file="$2"

project_path="./projects/$project_name"

# If requirements.txt does not exist, we stop program with exit status 2
if ! [ -f "$project_path/requirements.txt" ]; then
    echo -e "\nCannot proceed, requirements.txt does not exist at $project_path/\n"
    exit 2
fi


# We create a venv if it doesn't exist
if ! [ -d "./$project_path/.venv" ]; then
    echo -e "\nvenv does not exist, creating it at $project_path/.venv\n"
    python3 -m venv "$project_path/.venv"
    sleep 0.5

    # If we cannot creatr it, we return a status code 3
    if ! [ -d "$project_path/.venv" ]; then
    echo -e "\nCould not create .venv, check your python or permissions.\n"
    exit 3
    fi
fi

# Then we activate it
source "$project_path/.venv/bin/activate"
echo -e "\nvenv activated\n"


# We install dependencies
pip install -r "$project_path/requirements.txt"

# Running tests
pytest "$project_path/$test_file"


