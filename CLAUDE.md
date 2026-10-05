# Red Gate — project context

"Red Gate" is a GitLab Duo Agent Platform hackathon project (GitLab "Life After Code"
Transcend Hackathon, Path A "Start Fresh", Hands-off autonomy). It is an autonomous
DevSecOps loop: a red-team agent must FAIL to break the app before CI promotes it to
production.

## Rules (read first)

- `app/` is a DELIBERATELY VULNERABLE FastAPI target. The three planted vulns are the
  demo material:
  - VULN-1: SQL injection in `/login`
  - VULN-2: missing authorization on `/admin/users`
  - VULN-3: hardcoded secret (`API_KEY`) in `app/main.py`
- NEVER fix these in `app/main.py`. The pipeline and the defender agent fix them at
  runtime. If you think a vuln needs fixing, stop and ask.
- `tests/` is the `verify` stage and must keep passing after any fix.
- Don't add or remove `# noqa: REDGATE-VULN-n` markers; the demo points at them.
- Keep all AI/agent calls server-side.

## Layout

| Path | Role |
|------|------|
| `app/` | Vulnerable FastAPI target (`main.py`, SQLite layer in `db.py`) |
| `tests/` | Functional tests (health, valid/invalid login) |
| `security/redteam.py` | Adversarial gate. Attacks a deployed URL; exit 1 = breach, blocks promotion |
| `.gitlab-ci.yml` | Pipeline: tests → sast/secret_detection → build-image → deploy-staging (Cloud Run) → redteam → deploy-prod (default branch only) |
| `flows/` | GitLab Duo Agent Platform flow (agentic layer). Referenced in README, not yet present |

## Stack

Python 3.12 / FastAPI / SQLite, httpx for the red team, pytest, Docker, Cloud Run.

## Commands

```bash
pip install -r requirements.txt
pytest -q
uvicorn app.main:app --reload --port 8099
python security/redteam.py --base-url http://127.0.0.1:8099   # expect GATE: FAIL on baseline
```

CI variables: `GCP_PROJECT`, `GCP_REGION`, `GCP_SA_KEY` (`CI_REGISTRY*` are automatic).

## Known caveats

- `redteam.py` treats a failed request (target down) as "held", so it fails open.
- The VULN-3 runtime probe never finds the key even on the baseline; static Secret
  Detection is what catches it.
