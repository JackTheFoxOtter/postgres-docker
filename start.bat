@echo off

Rem Create required datafolders (these are mounted into the containers).
Rem On Windows we don't need to worry about file ownership here.

docker compose up --build