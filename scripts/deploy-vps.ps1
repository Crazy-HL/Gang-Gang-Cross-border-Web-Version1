[CmdletBinding()]
param(
  [string]$HostAlias = "GGKJ",
  [string]$RepoUrl = "https://github.com/Crazy-HL/Gang-Gang-Cross-border-Web-Version1.git",
  [string]$Branch = "master",
  [string]$RemoteRepoDir = "/opt/ggkj-web-repo",
  [string]$RemoteAppDir = "/opt/ggkj-web",
  [string]$RemoteSiteDir = "/opt/1panel/www/sites/ggkj-ip/index",
  [string]$BackendService = "ggkj-web-backend",
  [switch]$SkipLocalChecks,
  [switch]$PlanOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

function Invoke-RepoGit {
  param([string[]]$Arguments)

  $output = & git -C $RepoRoot @Arguments 2>&1
  if ($LASTEXITCODE -ne 0) {
    throw "git $($Arguments -join ' ') failed:`n$($output -join "`n")"
  }
  return ($output -join "`n")
}

function ConvertTo-BashSingleQuoted {
  param([string]$Value)

  if ($Value.Contains("'")) {
    throw "Values containing single quotes are not supported: $Value"
  }
  return "'$Value'"
}

if (-not $SkipLocalChecks) {
  $dirty = Invoke-RepoGit @("status", "--porcelain")
  if ($dirty.Trim().Length -gt 0) {
    throw @"
Local repository has uncommitted changes.
Commit and push your work before deployment, or rerun with -SkipLocalChecks if you intentionally want to deploy GitHub's current state.

$dirty
"@
  }

  $currentBranch = (Invoke-RepoGit @("branch", "--show-current")).Trim()
  if ($currentBranch -ne $Branch) {
    throw "Current branch is '$currentBranch', but this deployment targets '$Branch'."
  }

  Invoke-RepoGit @("fetch", "origin", $Branch) | Out-Null
  $localHead = (Invoke-RepoGit @("rev-parse", "HEAD")).Trim()
  $remoteHead = (Invoke-RepoGit @("rev-parse", "origin/$Branch")).Trim()
  if ($localHead -ne $remoteHead) {
    throw @"
Your local HEAD is not the same as origin/$Branch.
Push your latest commit first, then deploy.

local : $localHead
origin: $remoteHead
"@
  }
}

Write-Host "Deploy target:"
Write-Host "  host        : $HostAlias"
Write-Host "  repo        : $RepoUrl"
Write-Host "  branch      : $Branch"
Write-Host "  remote repo : $RemoteRepoDir"
Write-Host "  remote app  : $RemoteAppDir"
Write-Host "  static root : $RemoteSiteDir"
Write-Host "  service     : $BackendService"

if ($PlanOnly) {
  Write-Host "PlanOnly is set; no SSH commands were run."
  exit 0
}

$repoUrlQ = ConvertTo-BashSingleQuoted $RepoUrl
$branchQ = ConvertTo-BashSingleQuoted $Branch
$remoteRepoDirQ = ConvertTo-BashSingleQuoted $RemoteRepoDir
$remoteAppDirQ = ConvertTo-BashSingleQuoted $RemoteAppDir
$remoteSiteDirQ = ConvertTo-BashSingleQuoted $RemoteSiteDir
$backendServiceQ = ConvertTo-BashSingleQuoted $BackendService

$remoteScriptTemplate = @'
set -euo pipefail

REPO_URL=__REPO_URL__
BRANCH=__BRANCH__
REMOTE_REPO_DIR=__REMOTE_REPO_DIR__
REMOTE_APP_DIR=__REMOTE_APP_DIR__
REMOTE_SITE_DIR=__REMOTE_SITE_DIR__
BACKEND_SERVICE=__BACKEND_SERVICE__

log() {
  printf '\n==> %s\n' "$1"
}

ensure_empty_or_git_repo_dir() {
  local dir="$1"
  if [ ! -e "$dir" ]; then
    sudo mkdir -p "$dir"
    sudo chown "$USER:$USER" "$dir"
    return
  fi
  if [ ! -d "$dir" ]; then
    echo "Remote repo path exists but is not a directory: $dir" >&2
    exit 1
  fi
  if [ -d "$dir/.git" ]; then
    return
  fi
  if [ -z "$(find "$dir" -mindepth 1 -maxdepth 1 -print -quit)" ]; then
    sudo chown "$USER:$USER" "$dir"
    return
  fi
  echo "Remote repo dir exists but is not empty and not a git repo: $dir" >&2
  exit 1
}

log "Preparing source checkout"
ensure_empty_or_git_repo_dir "$REMOTE_REPO_DIR"

if [ -d "$REMOTE_REPO_DIR/.git" ]; then
  cd "$REMOTE_REPO_DIR"
  git remote set-url origin "$REPO_URL"
  git fetch origin "$BRANCH"
  git checkout "$BRANCH" 2>/dev/null || git checkout -B "$BRANCH" "origin/$BRANCH"
  git pull --ff-only origin "$BRANCH"
else
  git clone --branch "$BRANCH" "$REPO_URL" "$REMOTE_REPO_DIR"
fi

DEPLOY_COMMIT="$(git -C "$REMOTE_REPO_DIR" rev-parse HEAD)"
SHORT_COMMIT="$(git -C "$REMOTE_REPO_DIR" rev-parse --short HEAD)"
echo "Deploying commit $SHORT_COMMIT"

log "Syncing source into app directory"
if [ ! -d "$REMOTE_APP_DIR" ]; then
  sudo mkdir -p "$REMOTE_APP_DIR"
  sudo chown "$USER:$USER" "$REMOTE_APP_DIR"
fi

if [ ! -f "$REMOTE_APP_DIR/backend/.env" ]; then
  echo "Missing $REMOTE_APP_DIR/backend/.env; refusing to deploy without the VPS environment file." >&2
  exit 1
fi

if ! command -v rsync >/dev/null 2>&1; then
  sudo apt-get update
  sudo apt-get install -y rsync
fi

rsync -a --delete \
  --exclude ".git/" \
  --exclude "backend/.env" \
  --exclude "backend/.venv/" \
  --exclude "backend/uploads/" \
  --exclude "frontend/node_modules/" \
  --exclude "frontend/dist/" \
  "$REMOTE_REPO_DIR"/ "$REMOTE_APP_DIR"/

log "Installing backend dependencies"
cd "$REMOTE_APP_DIR/backend"
if [ ! -x ".venv/bin/python" ]; then
  if command -v python3.12 >/dev/null 2>&1; then
    python3.12 -m venv .venv
  else
    python3 -m venv .venv
  fi
fi
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt

log "Building frontend"
cd "$REMOTE_APP_DIR/frontend"
npm ci
npm run build

log "Publishing frontend assets"
resolved_site_dir="$(readlink -f "$REMOTE_SITE_DIR")"
if [ "$resolved_site_dir" != "$REMOTE_SITE_DIR" ]; then
  echo "Static root resolved unexpectedly: $resolved_site_dir" >&2
  exit 1
fi
if [ ! -d "$REMOTE_SITE_DIR" ]; then
  echo "Static root does not exist: $REMOTE_SITE_DIR" >&2
  exit 1
fi
sudo find "$REMOTE_SITE_DIR" -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
sudo cp -a "$REMOTE_APP_DIR/frontend/dist/." "$REMOTE_SITE_DIR/"

log "Restarting backend"
printf '%s\n' "$DEPLOY_COMMIT" | sudo tee "$REMOTE_APP_DIR/.deployed-commit" >/dev/null
sudo systemctl restart "$BACKEND_SERVICE"
sudo systemctl is-active "$BACKEND_SERVICE"

log "Verifying deployment"
curl -fsS http://127.0.0.1:8000/health >/dev/null
curl -fsS -o /dev/null http://127.0.0.1/
echo "Deployment finished: $SHORT_COMMIT"
'@

$remoteScript = $remoteScriptTemplate.
  Replace("__REPO_URL__", $repoUrlQ).
  Replace("__BRANCH__", $branchQ).
  Replace("__REMOTE_REPO_DIR__", $remoteRepoDirQ).
  Replace("__REMOTE_APP_DIR__", $remoteAppDirQ).
  Replace("__REMOTE_SITE_DIR__", $remoteSiteDirQ).
  Replace("__BACKEND_SERVICE__", $backendServiceQ)

$remoteScript | & ssh $HostAlias "bash -s"
if ($LASTEXITCODE -ne 0) {
  throw "Remote deployment failed."
}
