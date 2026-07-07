#!/usr/bin/env bash
set -euo pipefail

OLD_SSH_USER="${OLD_SSH_USER:-root}"
OLD_SSH_HOST="${OLD_SSH_HOST:-8.145.44.148}"
OLD_SSH_PORT="${OLD_SSH_PORT:-22}"

NEW_SSH_USER="${NEW_SSH_USER:-ubuntu}"
NEW_SSH_HOST="${NEW_SSH_HOST:-62.234.77.140}"
NEW_SSH_PORT="${NEW_SSH_PORT:-22}"

DB_NAME="${DB_NAME:-ggkj}"
APP_DB_USER="${APP_DB_USER:-ggkj}"

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$PROJECT_ROOT/backend/.env"
BACKUP_DIR="$PROJECT_ROOT/.migration-backups"
TS="$(date +%Y%m%d%H%M%S)"
LOCAL_DUMP="$BACKUP_DIR/ggkj_live_migration_${TS}.sql.gz"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing env file: $ENV_FILE" >&2
  exit 1
fi

APP_DB_PASSWORD="$(
  python3 - "$ENV_FILE" <<'PY'
from pathlib import Path
from urllib.parse import urlparse, unquote
import sys

for raw in Path(sys.argv[1]).read_text().splitlines():
    if raw.startswith("GANGGANG_DATABASE_URL="):
        value = raw.split("=", 1)[1].strip().strip('"').strip("'")
        print(unquote(urlparse(value).password or ""))
        break
PY
)"

if [[ -z "$APP_DB_PASSWORD" ]]; then
  echo "Could not read database password from $ENV_FILE" >&2
  exit 1
fi

mkdir -p "$BACKUP_DIR"

echo "== Step 1: Dump old database =="
ssh -p "$OLD_SSH_PORT" "$OLD_SSH_USER@$OLD_SSH_HOST" \
  "MYSQL_PWD='$APP_DB_PASSWORD' mysqldump \
    -h 8.145.44.148 -P 3306 -u '$APP_DB_USER' \
    --single-transaction --quick --routines --triggers --no-tablespaces \
    --default-character-set=utf8mb4 --databases '$DB_NAME' | gzip -9" \
  > "$LOCAL_DUMP"

gzip -t "$LOCAL_DUMP"
shasum -a 256 "$LOCAL_DUMP"

echo "== Step 2: Upload dump to new server =="
REMOTE_DUMP="/tmp/$(basename "$LOCAL_DUMP")"
scp -P "$NEW_SSH_PORT" "$LOCAL_DUMP" "$NEW_SSH_USER@$NEW_SSH_HOST:$REMOTE_DUMP"

echo "== Step 3: Import on new server =="
ssh -p "$NEW_SSH_PORT" "$NEW_SSH_USER@$NEW_SSH_HOST" "REMOTE_DUMP='$REMOTE_DUMP' DB_NAME='$DB_NAME' APP_DB_USER='$APP_DB_USER' APP_DB_PASSWORD='$APP_DB_PASSWORD' bash -s" <<'REMOTE'
set -euo pipefail

if command -v docker >/dev/null 2>&1 && sudo docker ps --format '{{.Names}} {{.Image}}' | grep -Ei 'mysql|mariadb' >/dev/null; then
  MYSQL_CONTAINER="$(sudo docker ps --format '{{.Names}} {{.Image}}' | awk 'tolower($0) ~ /mysql|mariadb/ {print $1; exit}')"
  ROOT_PASSWORD="$(sudo docker inspect "$MYSQL_CONTAINER" --format '{{range .Config.Env}}{{println .}}{{end}}' | grep '^MYSQL_ROOT_PASSWORD=' | sed 's/^MYSQL_ROOT_PASSWORD=//')"

  if [[ -z "$ROOT_PASSWORD" ]]; then
    echo "MySQL container found, but MYSQL_ROOT_PASSWORD env is missing." >&2
    exit 1
  fi

  gunzip -c "$REMOTE_DUMP" | sudo docker exec -i -e MYSQL_PWD="$ROOT_PASSWORD" "$MYSQL_CONTAINER" mysql -uroot --default-character-set=utf8mb4
  sudo docker exec -i -e MYSQL_PWD="$ROOT_PASSWORD" "$MYSQL_CONTAINER" mysql -uroot --default-character-set=utf8mb4 <<SQL
CREATE DATABASE IF NOT EXISTS \`$DB_NAME\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '$APP_DB_USER'@'%' IDENTIFIED BY '$APP_DB_PASSWORD';
ALTER USER '$APP_DB_USER'@'%' IDENTIFIED BY '$APP_DB_PASSWORD';
CREATE USER IF NOT EXISTS '$APP_DB_USER'@'localhost' IDENTIFIED BY '$APP_DB_PASSWORD';
ALTER USER '$APP_DB_USER'@'localhost' IDENTIFIED BY '$APP_DB_PASSWORD';
GRANT ALL PRIVILEGES ON \`$DB_NAME\`.* TO '$APP_DB_USER'@'%';
GRANT ALL PRIVILEGES ON \`$DB_NAME\`.* TO '$APP_DB_USER'@'localhost';
FLUSH PRIVILEGES;
SQL
  sudo docker exec -e MYSQL_PWD="$APP_DB_PASSWORD" "$MYSQL_CONTAINER" mysql -u"$APP_DB_USER" -D "$DB_NAME" -N -e "SELECT COUNT(*) FROM users; SELECT COUNT(*) FROM jobs; SELECT COUNT(*) FROM reports; SELECT COUNT(*) FROM job_files;"
else
  if ! command -v mysql >/dev/null 2>&1; then
    sudo apt-get update
    sudo DEBIAN_FRONTEND=noninteractive apt-get install -y mysql-server
    sudo systemctl enable --now mysql
  fi

  gunzip -c "$REMOTE_DUMP" | sudo mysql --default-character-set=utf8mb4
  sudo mysql --default-character-set=utf8mb4 <<SQL
CREATE DATABASE IF NOT EXISTS \`$DB_NAME\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '$APP_DB_USER'@'%' IDENTIFIED BY '$APP_DB_PASSWORD';
ALTER USER '$APP_DB_USER'@'%' IDENTIFIED BY '$APP_DB_PASSWORD';
CREATE USER IF NOT EXISTS '$APP_DB_USER'@'localhost' IDENTIFIED BY '$APP_DB_PASSWORD';
ALTER USER '$APP_DB_USER'@'localhost' IDENTIFIED BY '$APP_DB_PASSWORD';
GRANT ALL PRIVILEGES ON \`$DB_NAME\`.* TO '$APP_DB_USER'@'%';
GRANT ALL PRIVILEGES ON \`$DB_NAME\`.* TO '$APP_DB_USER'@'localhost';
FLUSH PRIVILEGES;
SQL
  MYSQL_PWD="$APP_DB_PASSWORD" mysql -h 127.0.0.1 -P 3306 -u"$APP_DB_USER" -D "$DB_NAME" -N -e "SELECT COUNT(*) FROM users; SELECT COUNT(*) FROM jobs; SELECT COUNT(*) FROM reports; SELECT COUNT(*) FROM job_files;"
fi

rm -f "$REMOTE_DUMP"
REMOTE

echo "== Done =="
echo "Local backup kept at: $LOCAL_DUMP"
