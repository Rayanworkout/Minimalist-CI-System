#!/bin/bash

set -e # exit program if a command returns a non-zero status

project_name="$1"

project_folder="./projects/$project_name"

if [ -d "$project_folder" ]; then
    echo -e "\n$1 exists, pulling latest changes\n"
    cd "$project_folder"
    git pull origin main

else
    echo -e "\n$project_name does not exist, please run clone_project.sh first\n"
fi