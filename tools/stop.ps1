if ($PSVersionTable.PSEdition -ne "CORE") { Throw "PowerShell Core is required to run this script!" }

# Stops the container
docker compose down