if ($PSVersionTable.PSEdition -ne "CORE") { Throw "PowerShell Core is required to run this script!" }

# Start the container detached and attach 
docker compose up -d; docker compose logs -f