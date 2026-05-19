"""Thin query/parse helper over the local roborev daemon.

The CLI (`roborev list --json`, `roborev show --json`) already returns rich
JSON. This helper exists to normalize one thing the CLI doesn't expose
structurally—the `output` field's markdown findings—and to provide
condensed, stable JSON for SKILL.md bodies to consume.

Subcommands:

    open [--branch <name>] [--repo <path>] [--limit N]
        List open review jobs as condensed JSON:
        [{job_id, review_id, branch, commit_sha, commit_subject,
          repo_name, verdict, severity_top, agent}, ...]

    parse <job_id_or_sha>
        Fetch the review for the given job_id or commit sha and emit:
        {job_id, review_id, commit_sha, branch, repo_name, verdict,
         summary, findings: [{severity, locations, problem, fix}, ...]}
        Severity normalized to one of: critical|high|medium|low|info|unknown.

    histogram [--branch <name>] [--repo <path>]
        Count open reviews by top-severity:
        {critical: N, high: N, medium: N, low: N, info: N, unknown: N, total: N}

Exit codes:
    0  success
    1  daemon unreachable or no matching review
    2  bad arguments
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from typing import Any

ROBOREV = "roborev"


SEVERITY_NORMAL = {
    "critical": "critical",
    "high": "high",
    "medium": "medium",
    "med": "medium",
    "low": "low",
    "info": "info",
    "informational": "info",
}

SEVERITY_RANK = {
    "critical": 5,
    "high": 4,
    "medium": 3,
    "low": 2,
    "info": 1,
    "unknown": 0,
}


def run_roborev(args: list[str]) -> tuple[int, str, str]:
    """Run roborev with the given args; return (exit_code, stdout, stderr)."""
    try:
        proc = subprocess.run(
            [ROBOREV] + args,
            capture_output=True,
            text=True,
            timeout=60,
        )
    except FileNotFoundError:
        print("roborev binary not on PATH", file=sys.stderr)
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print("roborev call timed out after 60s", file=sys.stderr)
        sys.exit(1)
    return proc.returncode, proc.stdout, proc.stderr


def normalize_severity(s: str) -> str:
    key = (s or "").strip().lower().rstrip(":").rstrip("*").strip()
    return SEVERITY_NORMAL.get(key, "unknown")


# Findings are emitted by roborev's agent as markdown blocks like:
#
#   ## Review Findings
#   - **Severity**: Medium
#     **Location**: `file.py:545`, `file.py:672`
#     **Problem**: ...
#     **Fix**: ...
#
# We split on each "Severity:" header and extract the four fields per block.

SEVERITY_HEADER_RE = re.compile(
    r"""
    [-*]?\s*                          # optional list bullet
    \*\*Severity\*\*\s*:\s*           # **Severity**:
    (?P<sev>[A-Za-z]+)                # one word
    """,
    re.VERBOSE,
)


def parse_findings_markdown(output: str) -> tuple[list[dict[str, Any]], str]:
    """Parse the `output` field of a review into (findings, summary)."""
    if not output:
        return [], ""
    if output.strip().startswith("No issues found"):
        # extract optional Summary line
        m = re.search(r"Summary:\s*(.+)", output)
        return [], m.group(1).strip() if m else ""

    # Split by "## Summary" first to isolate findings vs summary.
    summary = ""
    if "## Summary" in output:
        body, _, summary_part = output.partition("## Summary")
        summary = summary_part.strip()
    else:
        body = output

    # Each finding starts with a "**Severity**:" header. Split on those.
    splits = list(SEVERITY_HEADER_RE.finditer(body))
    findings: list[dict[str, Any]] = []
    for i, m in enumerate(splits):
        start = m.start()
        end = splits[i + 1].start() if i + 1 < len(splits) else len(body)
        block = body[start:end]
        severity = normalize_severity(m.group("sev"))

        loc = _extract_field(block, "Location")
        problem = _extract_field(block, "Problem")
        fix = _extract_field(block, "Fix")
        findings.append(
            {
                "severity": severity,
                "locations": _split_locations(loc),
                "problem": problem,
                "fix": fix,
            }
        )

    return findings, summary


FIELD_RE_TEMPLATE = r"\*\*{name}\*\*\s*:\s*(?P<val>.+?)(?=\n\s*[-*]?\s*\*\*[A-Z][A-Za-z]+\*\*\s*:|\n\s*##|\Z)"


def _extract_field(block: str, name: str) -> str:
    pat = re.compile(FIELD_RE_TEMPLATE.format(name=name), re.DOTALL)
    m = pat.search(block)
    if not m:
        return ""
    return _strip_trailing_whitespace(m.group("val"))


def _strip_trailing_whitespace(s: str) -> str:
    return "\n".join(line.rstrip() for line in s.strip().splitlines())


LOCATION_TOKEN_RE = re.compile(
    r"""
    (?:`(?P<bt>[^`]+)`)                 # backticked: `file.py:123`
    |
    (?:\[(?P<label>[^\]]+)\]\([^)]+\))  # markdown link: [file.py:123](url)
    |
    (?:(?P<plain>[A-Za-z0-9_./-]+(?::\d+)?))
    """,
    re.VERBOSE,
)


def _split_locations(loc_str: str) -> list[str]:
    if not loc_str:
        return []
    out: list[str] = []
    for m in LOCATION_TOKEN_RE.finditer(loc_str):
        token = m.group("bt") or m.group("label") or m.group("plain")
        if token and re.search(r"[./:]", token):
            out.append(token)
    # de-dup preserving order
    seen: set[str] = set()
    return [x for x in out if not (x in seen or seen.add(x))]


def top_severity(findings: list[dict[str, Any]]) -> str:
    if not findings:
        return "none"
    return max((f["severity"] for f in findings), key=lambda s: SEVERITY_RANK.get(s, 0))


def cmd_open(args: argparse.Namespace) -> int:
    cli = ["list", "--json", "--open", "--limit", str(args.limit)]
    if args.branch:
        cli += ["--branch", args.branch]
    if args.repo:
        cli += ["--repo", args.repo]
    code, out, err = run_roborev(cli)
    if code != 0:
        print(err.strip() or f"roborev list failed (exit {code})", file=sys.stderr)
        return 1
    raw = out.strip()
    if not raw or raw == "null":
        print("[]")
        return 0
    jobs = json.loads(raw)
    condensed: list[dict[str, Any]] = []
    for job in jobs:
        job_id = job.get("id") or job.get("job_id")
        if job_id is None:
            continue
        # Pull the review (may be cheap; cached in daemon).
        ec, jout, _jerr = run_roborev(["show", "--json", "--job", str(job_id)])
        if ec != 0:
            continue
        try:
            envelope = json.loads(jout)
        except json.JSONDecodeError:
            continue
        review_id = envelope.get("id")
        findings, _summary = parse_findings_markdown(envelope.get("output", ""))
        meta = envelope.get("job", {})
        condensed.append(
            {
                "job_id": job_id,
                "review_id": review_id,
                "branch": meta.get("branch"),
                "commit_sha": meta.get("git_ref"),
                "commit_subject": meta.get("commit_subject"),
                "repo_name": meta.get("repo_name"),
                "verdict": meta.get("verdict"),
                "agent": meta.get("agent"),
                "severity_top": top_severity(findings),
                "finding_count": len(findings),
            }
        )
    print(json.dumps(condensed, indent=2))
    return 0


def cmd_parse(args: argparse.Namespace) -> int:
    cli = ["show", "--json"]
    if args.job:
        cli += ["--job", str(args.target)]
    else:
        cli += [str(args.target)]
    code, out, err = run_roborev(cli)
    if code != 0:
        print(err.strip() or f"roborev show failed (exit {code})", file=sys.stderr)
        return 1
    envelope = json.loads(out)
    findings, summary = parse_findings_markdown(envelope.get("output", ""))
    meta = envelope.get("job", {})
    print(
        json.dumps(
            {
                "job_id": envelope.get("job_id"),
                "review_id": envelope.get("id"),
                "commit_sha": meta.get("git_ref"),
                "branch": meta.get("branch"),
                "repo_name": meta.get("repo_name"),
                "verdict": meta.get("verdict"),
                "summary": summary,
                "findings": findings,
            },
            indent=2,
        )
    )
    return 0


def cmd_histogram(args: argparse.Namespace) -> int:
    cli = ["list", "--json", "--open", "--limit", str(args.limit)]
    if args.branch:
        cli += ["--branch", args.branch]
    if args.repo:
        cli += ["--repo", args.repo]
    code, out, err = run_roborev(cli)
    if code != 0:
        print(err.strip() or f"roborev list failed (exit {code})", file=sys.stderr)
        return 1
    raw = out.strip()
    jobs = [] if not raw or raw == "null" else json.loads(raw)
    counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0, "unknown": 0}
    for job in jobs:
        job_id = job.get("id") or job.get("job_id")
        if job_id is None:
            continue
        ec, jout, _ = run_roborev(["show", "--json", "--job", str(job_id)])
        if ec != 0:
            continue
        envelope = json.loads(jout)
        for f in parse_findings_markdown(envelope.get("output", ""))[0]:
            counts[f["severity"]] = counts.get(f["severity"], 0) + 1
    counts["total"] = sum(v for k, v in counts.items() if k != "total")
    print(json.dumps(counts, indent=2))
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    sp_open = sub.add_parser("open", help="list open jobs (condensed JSON)")
    sp_open.add_argument("--branch", default=None)
    sp_open.add_argument("--repo", default=None)
    sp_open.add_argument("--limit", type=int, default=50)
    sp_open.set_defaults(func=cmd_open)

    sp_parse = sub.add_parser("parse", help="parse a single job's review output")
    sp_parse.add_argument("target", help="job_id or commit sha")
    sp_parse.add_argument("--job", action="store_true", help="force target as job_id")
    sp_parse.set_defaults(func=cmd_parse)

    sp_hist = sub.add_parser("histogram", help="counts of open findings by severity")
    sp_hist.add_argument("--branch", default=None)
    sp_hist.add_argument("--repo", default=None)
    sp_hist.add_argument("--limit", type=int, default=50)
    sp_hist.set_defaults(func=cmd_histogram)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
