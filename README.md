# Red Gate

**An autonomous DevSecOps pipeline where a red-team agent has to fail to break the app before it's allowed to ship.**

Built for the GitLab "Life After Code" Transcend Hackathon — Path A (Start Fresh), Hands-off autonomy.

## The idea

Code generation is solved. Red Gate automates everything *after* the code is
written, and adds an adversarial twist: the app is only promoted to production
once an attacker can no longer get in.

```
issue ──▶ plan ──▶ build (MR) ──▶ verify ──▶ scan ──▶ package
                                                          │
                              ┌───────────────────────────┘
                              ▼
                      deploy to staging
                              │
                              ▼
                    ╔═════════════════╗   breach found
                    ║  RED-TEAM GATE  ║──────────────┐
                    ╚═════════════════╝              ▼
                              │ held           defender agent
                              ▼                 patches + retests
                      deploy to prod                 │
                              │                       │
                              ▼                       └──▶ (loop)
                        monitor + govern
```

## DevSecOps stages covered

`plan` · `create` · `verify` · `package` · `secure` · `release` · `configure` · `monitor` · `govern` — all nine.

## Repo layout

| Path | Role |
|------|------|
| `app/` | Deliberately vulnerable FastAPI target app (the thing that gets built, attacked, fixed) |
| `tests/` | Functional tests — the `verify` stage |
| `security/redteam.py` | The adversarial gate — active attacks against staging; non-zero exit blocks promotion |
| `.gitlab-ci.yml` | Deterministic pipeline spine |
| `flows/` | GitLab Duo Agent Platform flow (the agentic reasoning layer) |

## Planted vulnerabilities (baseline state)

The target app ships intentionally vulnerable so the pipeline has something real
to find on camera:

- **VULN-1** SQL injection auth bypass in `/login` → caught by SAST **and** the red-team gate
- **VULN-2** missing authorization on `/admin/users` → caught by the red-team gate at runtime
- **VULN-3** hardcoded secret in source → caught by GitLab Secret Detection (static)

## Run it locally

```bash
pip install -r requirements.txt

# functional tests
pytest -q

# run the app
uvicorn app.main:app --reload --port 8099

# attack it (expect GATE: FAIL against the vulnerable baseline)
python security/redteam.py --base-url http://127.0.0.1:8099
```

## CI/CD variables required

| Variable | Purpose |
|----------|---------|
| `GCP_PROJECT` | Google Cloud project ID |
| `GCP_REGION` | Cloud Run region (for the deploy bonus) |
| `GCP_SA_KEY` | Service-account JSON key |

`CI_REGISTRY*` are provided by GitLab automatically.

## License

MIT — see [LICENSE](LICENSE).
