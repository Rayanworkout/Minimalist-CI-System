#!/bin/bash

set -e # exit program if a command returns a non-zero status

# If projects folder does not exist, we create it
if ! [ -d "./projects" ]; then
    echo -e "\nProjects folder does not exist. Creating it.\n"
    mkdir ./projects
fi

project_folder="./projects/$1"

if ! [ -d "$project_folder" ]; then
    # We clone the project inside the projects folder
    git clone "$2" "$project_folder"

else
    echo -e "\n$1 already exists, please run pull_latest_changes.sh instead\n"
fi