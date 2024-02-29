#!/bin/bash

set -e # exit program if a command returns a non-zero status

# If projects folder does not exist, we create it
if ! [ -d "./projects" ]; then
    echo -e "\nProjects folder does not exist. Creating it.\n"
    mkdir ./projects
fi

project_folder="./projects/$1"

if [ -d "$project_folder" ]; then
    echo -e "\n$1 exists, pulling latest changes\n"
    cd "$project_folder"
    git pull origin main

else
    # We clone the project inside the projects folder
    git clone "$2" "$project_folder"
fi