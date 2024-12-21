if ($PSVersionTable.PSEdition -ne "CORE") { Throw "PowerShell Core is required to run this script!" }

# Build the container & inject current date as the build arg
docker compose build --build-arg ("BUILDDATE=" + (get-date -uformat '%Y-%m-%d %H:%M:%S').ToString()) $args
