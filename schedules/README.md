# Schedules

Documented cron / launchd entries you install manually. These are *not* loaded automatically by anything in this repo — they're recipes you run when you want them.

## Why not the `schedule` skill?

The Claude Code `schedule` skill creates *remote scheduled agents* that fire inside a Claude session. That's the right fit when the work is "ask Claude to do something on a cadence." It is the wrong fit for werk-infra tasks that need to run whether or not a Claude session exists — regenerating transcripts, sanity-checking builds, nightly drift detection. Those go in cron or launchd.

## Recipes

Each recipe below is presented in two forms: a one-line `crontab` entry and an equivalent `launchd` plist. Pick one. Don't install both for the same task.

### Nightly: regenerate transcripts for changed lessons

Runs once a day, walks every werk project, regenerates transcripts for lessons whose `.py` is newer than the matching `examples/NN_*.md`. Adapt the project list.

**cron** (`crontab -e`, fires at 02:30 local):

```cron
30 2 * * * /Users/bill/projects/dehora/skills/schedules/nightly-transcript-refresh.sh >> /tmp/werk-nightly.log 2>&1
```

**launchd** (`~/Library/LaunchAgents/net.dehora.werk.nightly-transcript.plist`):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>            <string>net.dehora.werk.nightly-transcript</string>
  <key>ProgramArguments</key>
  <array>
    <string>/Users/bill/projects/dehora/skills/schedules/nightly-transcript-refresh.sh</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Hour</key>   <integer>2</integer>
    <key>Minute</key> <integer>30</integer>
  </dict>
  <key>StandardOutPath</key>  <string>/tmp/werk-nightly.log</string>
  <key>StandardErrorPath</key><string>/tmp/werk-nightly.log</string>
  <key>RunAtLoad</key>        <false/>
</dict>
</plist>
```

Load with: `launchctl load ~/Library/LaunchAgents/net.dehora.werk.nightly-transcript.plist`

The `nightly-transcript-refresh.sh` shell script is intentionally not shipped here — write it once the lesson set stabilizes. A reasonable skeleton:

```bash
#!/usr/bin/env bash
set -euo pipefail
for project in /Users/bill/projects/dehora/{modelwerk,policywerk,bayeswerk}; do
  [[ -d "$project" ]] || continue
  cd "$project"
  for py in lessons/[0-9][0-9]_*.py; do
    stem="${py%.py}"; stem="${stem#lessons/}"
    md="examples/${stem}.md"
    [[ -f "$md" ]] || continue
    if [[ "$py" -nt "$md" ]]; then
      uv run python /Users/bill/projects/dehora/skills/skills/lesson-transcript/scripts/run_lesson.py "$py"
    fi
  done
done
```

### Weekly: layering audit

```cron
0 9 * * 1 cd /Users/bill/projects/dehora/modelwerk && uv run python /Users/bill/projects/dehora/skills/skills/check-layering/scripts/check_layering.py src/modelwerk >> /tmp/werk-layering.log 2>&1
```

### One-shots inside Claude

For "run this once tomorrow at 9am from inside a Claude session," use the `schedule` skill (`/schedule`). For "run this from cron on my laptop while Claude is off," use the entries above.

## Notes

- These recipes assume `uv` is on the system `$PATH` for the user account that owns the cron job. If it isn't, prefix with `PATH=/Users/bill/.local/bin:$PATH` or call `uv` by absolute path.
- launchd jobs that depend on the user's keychain (e.g. for git push) require `SessionCreate` and an active GUI session — keep these workloads local-only (no push) unless you've already worked through the keychain unlock.
- Log to `/tmp/` deliberately — these are diagnostic logs, not artifacts. Promote to a checked-in log path once a recipe earns its keep.
