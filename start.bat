@echo off

Rem On Windows we don't worry about permissions (I think).
Rem Missing data folders will be owned by user / group 1000 by default.

docker compose up --build