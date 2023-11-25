@echo off

Rem Create required datafolders (these are mounted into the containers).
Rem On Windows we don't need to worry about file ownership here.
set datafolders=("postgres" "backups" "logs")
for %%f in %datafolders% do (
    mkdir "./data/%%f"
)

docker compose up --build