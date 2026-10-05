# Red Gate demo runbook (target: under 3:00)

The story in one line: **the pipeline refuses to ship the app until the red team
can no longer break in.** The two beats the video must land are the gate
**blocking** promotion, then **passing** after the defender's fix.

## Before you record (not on camera)

- [ ] GitLab project has the CI/CD variables `GCP_PROJECT`, `GCP_REGION`,
      `GCP_SA_KEY` set, and the Duo flow from `flows/red-gate-flow.yml` is
      registered and enabled for the project. [fill in: how you trigger the flow
      from an issue in your Duo setup]
- [ ] Default branch is the vulnerable baseline (do not pre-fix anything).
- [ ] Rehearse offline: `bash demo/local-attack.sh` (prints `GATE: FAIL`, exits 1).
- [ ] Open tabs: the project's Issues page, Pipelines page, and the staging and
      prod Cloud Run URLs.
- [ ] A full pipeline takes longer than the video. **Pre-run it once and record
      each step live, cutting the waits** (or keep a finished pipeline open for
      the pass shot). Timings below are for the edited video, not wall-clock.

## Timeline

| Time | Beat | What to do / say |
|------|------|------------------|
| 0:00-0:15 | **Hook** | Show the README diagram. Say: "Code generation is solved. Red Gate automates everything after the code, and the app only ships once an attacker can't get in." |
| 0:15-0:35 | **Trigger** | Create a new issue with the text from `demo/seed-issue.md` ("Add a password reset endpoint"). Trigger the flow. Say: "One issue. No human after this point." |
| 0:35-1:00 | **Plan + build** | Show the supervisor delegating: planner posts the task list, builder opens a branch and an MR. Say: "The supervisor only delegates. Planner plans, builder builds." |
| 1:00-1:20 | **Verify + secure** | Open the MR pipeline: `tests` green, then `sast` and `secret_detection` run. Point at the findings in the MR security widget: SQL injection (VULN-1) and the hardcoded key (VULN-3). |
| 1:20-1:45 | **THE GATE BLOCKS** | Pipeline reaches `deploy-staging`, then `redteam`. Open the `redteam` job log. Show `[BREACH] VULN-1`, `[BREACH] VULN-2`, then `GATE: FAIL - 2 attack(s) succeeded. Promotion blocked.` Show `deploy-prod` never starting. Say: "The attacker got in, so production stays untouched." Hold this shot. |
| 1:45-2:15 | **Defender fixes** | Show the defender's MR notes: parameterized query, auth check on `/admin/users`, secret moved to an env var. Show `tests` still green after the fix. Say: "It fixed the findings and kept the tests passing." |
| 2:15-2:40 | **THE GATE PASSES** | New pipeline on the fixed MR. `redteam` log: both attacks `held`, `GATE: PASS - red team could not break in. Safe to promote.` Merge the MR. On the default branch, `deploy-prod` runs. Hold on the PASS line. |
| 2:40-2:55 | **Monitor + govern** | Monitor reports `/health` UP on the prod URL. Show the compliance audit note on the original issue: found, fixed, gate verdict. |
| 2:55-3:00 | **Close** | "Red Gate: nine DevSecOps stages, zero hands. Ships only when the red team fails." |

## Stage coverage to mention

`plan` (planner) · `create` (builder) · `verify` (tests) · `secure` (SAST, secret
detection, red-team gate, defender) · `package` (image build) · `release`
(staging, prod) · `configure` (Cloud Run deploys) · `monitor` (monitor agent) ·
`govern` (compliance note).

## Things to get right on camera

- **Why prod only deploys after the merge:** `deploy-prod` is restricted to the
  default branch. The MR pipeline proves the gate (staging + redteam); the merge
  pipeline promotes.
- **VULN-3 is caught statically.** The red-team job shows it as `held` (it never
  probes the key at runtime). Credit Secret Detection for it, not the red team.
- **Don't edit `app/main.py` by hand** to "help" the demo. The defender's fix is
  the point.

## Reset between takes

Close the MR, delete the feature branch, and reset the default branch to the
vulnerable baseline commit. Re-run `bash demo/local-attack.sh` to confirm the
baseline still prints `GATE: FAIL` before the next take.

## Offline rehearsal

```bash
bash demo/local-attack.sh
```

Starts the app on port 8099 (override with `PORT=...`), runs
`security/redteam.py`, prints the verdict, stops the app, and exits with the
gate's exit code. Expected on the baseline: `GATE: FAIL - 2 attack(s) succeeded.`
