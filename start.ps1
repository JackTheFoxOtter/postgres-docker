# On Windows we don't worry about permissions (I think).
# Missing data folders will be owned by user / group 1000 by default.

docker compose build --build-arg ("BUILDDATE=" + (get-date -uformat %s).ToString())
docker compose up
