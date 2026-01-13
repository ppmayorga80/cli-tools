#!/bin/bash

REPO_DIR=$1
REPO_NAME=$(basename $REPO_DIR)

LOG_FILE="/Users/pedro/git_cron_${REPO_NAME}.log"
SSH_KEY="/Users/pedro/.ssh/id_ed25519"
GIT="/opt/homebrew/bin/git"

cd "$REPO_DIR" || exit 1

$GIT add -A

if ! $GIT diff --cached --quiet; then
  $GIT commit -m "Automated weekly commit"
fi

GIT_SSH_COMMAND="/usr/bin/ssh -i $SSH_KEY -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new" \
$GIT push >> "$LOG_FILE" 2>&1

PUSH_STATUS=$?

if [ $PUSH_STATUS -eq 0 ]; then
  /usr/bin/osascript -e 'display notification "Git push OK" with title "GitHub Automation"'
else
  /usr/bin/osascript -e 'display notification "Git push FAILED (ver /tmp/turing_git_cron.log)" with title "GitHub Automation"'
fi
