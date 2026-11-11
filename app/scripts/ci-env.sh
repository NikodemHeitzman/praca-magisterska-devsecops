#!/usr/bin/env sh
# Create app/.env for a CI job from .env.example, with fresh random secrets
# (docs/adr/0023-uruchamianie-stosu-docker-compose.md).
#
# The values live only in the job: nothing is stored in the repository or in GitHub Secrets.
# Usage (from app/): sh scripts/ci-env.sh   then   docker compose up -d --build
# The DAST job reads the seed passwords back from .env.
set -eu

cd "$(dirname "$0")/.."

if [ -e .env ]; then
    echo "app/.env already exists; refusing to overwrite it" >&2
    exit 1
fi

rand() { openssl rand -hex "$1"; }

db_password=$(rand 24)
jwt_secret=$(rand 48)
alice=$(rand 24)
bob=$(rand 24)
admin=$(rand 24)

# Hide the values in the GitHub Actions log.
if [ "${GITHUB_ACTIONS:-}" = "true" ]; then
    for value in "$db_password" "$jwt_secret" "$alice" "$bob" "$admin"; do
        echo "::add-mask::$value"
    done
fi

umask 077
sed \
    -e "s|^POSTGRES_PASSWORD=.*|POSTGRES_PASSWORD=$db_password|" \
    -e "s|^DATABASE_URL=.*|DATABASE_URL=postgresql+psycopg://ticketing:$db_password@127.0.0.1:5432/ticketing|" \
    -e "s|^JWT_SECRET=.*|JWT_SECRET=$jwt_secret|" \
    -e "s|^SEED_ALICE_PASSWORD=.*|SEED_ALICE_PASSWORD=$alice|" \
    -e "s|^SEED_BOB_PASSWORD=.*|SEED_BOB_PASSWORD=$bob|" \
    -e "s|^SEED_ADMIN_PASSWORD=.*|SEED_ADMIN_PASSWORD=$admin|" \
    .env.example > .env

# Every placeholder must be filled; an empty value here means .env.example gained a new secret.
for name in POSTGRES_PASSWORD JWT_SECRET SEED_ALICE_PASSWORD SEED_BOB_PASSWORD SEED_ADMIN_PASSWORD; do
    if grep -q "^$name=\(change-me\)\?$" .env; then
        echo "$name was not filled in app/.env" >&2
        exit 1
    fi
done

echo "app/.env created with random values"
