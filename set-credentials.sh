# Run using "source set-credentials.sh"
# Please set this accordingly before using "./run.sh"

echo "Setting credentials for project"

echo "Setting Postgres Admin Credentials"
export POSTGRES_USER="postgres"
export POSTGRES_PASSWORD="postgres"

echo "Setting Grafana Postgres User (only SELECT rights to specific schemas inside postgres)"
export GF_PG_USER="gf_postgres"
export GF_PG_PASSWORD="gf_postgres"

echo "Grafana Admin Configs"
export GF_SECURITY_ADMIN_PASSWORD="IamTheAdmin"

echo "PGAdmin Configs"
export PGADMIN_DEFAULT_EMAIL="opinion-analyzer-crew@hu-berlin.de"
export PGADMIN_DEFAULT_PASSWORD="IamTheMasterOfTheData"
