if ($PSVersionTable.PSEdition -ne "CORE") { Throw "PowerShell Core is required to run this script!" }

# On Windows we don't worry about permissions (I think).
# Missing data folders will be owned by user / group 1000 by default.
docker compose build --build-arg ("BUILDDATE=" + (get-date -uformat %s).ToString()) && docker compose down && docker compose up
