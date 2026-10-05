"""
Red Gate adversarial gate.

Runs active attacks against a deployed instance of the target app and FAILS
(exit 1) if any attack succeeds. CI runs this against staging after deploy; a
non-zero exit blocks promotion to production. This is the adversarial gate at
the centre of the project: the app only ships once the red team can no longer
get in.

Usage:
    python security/redteam.py --base-url https://red-gate-staging.run.app

Only ever point this at your own deployed demo instance.
"""
import argparse
import sys

import httpx

TIMEOUT = 10.0


class Attack:
    def __init__(self, ident: str, name: str):
        self.ident = ident
        self.name = name
        self.broke_in = False
        self.detail = ""


def attack_sqli(base_url: str) -> Attack:
    """VULN-1: auth bypass via SQL injection in /login."""
    a = Attack("VULN-1", "SQL injection auth bypass on /login")
    payload = {"username": "admin", "password": "' OR '1'='1"}
    try:
        r = httpx.post(f"{base_url}/login", json=payload, timeout=TIMEOUT)
        if r.status_code == 200:
            a.broke_in = True
            a.detail = f"injection authenticated as {r.json().get('username')!r}"
        else:
            a.detail = f"rejected with {r.status_code}"
    except Exception as exc:  # network / target down
        a.detail = f"request failed: {exc}"
    return a


def attack_missing_authz(base_url: str) -> Attack:
    """VULN-2: unauthenticated access to /admin/users."""
    a = Attack("VULN-2", "Missing authz on /admin/users")
    try:
        r = httpx.get(f"{base_url}/admin/users", timeout=TIMEOUT)
        if r.status_code == 200 and "users" in r.text:
            a.broke_in = True
            n = len(r.json().get("users", []))
            a.detail = f"dumped {n} user record(s) with no auth"
        else:
            a.detail = f"blocked with {r.status_code}"
    except Exception as exc:
        a.detail = f"request failed: {exc}"
    return a


def attack_secret_leak(base_url: str) -> Attack:
    """VULN-3: the hardcoded key should never be reachable at runtime."""
    a = Attack("VULN-3", "Hardcoded secret exposure")
    for path in ("/", "/health", "/debug", "/config"):
        try:
            r = httpx.get(f"{base_url}{path}", timeout=TIMEOUT)
            if "sk-live-" in r.text:
                a.broke_in = True
                a.detail = f"secret string reachable at {path}"
                return a
        except Exception:
            continue
    a.detail = "no secret exposed at probed paths"
    return a


ATTACKS = [attack_sqli, attack_missing_authz, attack_secret_leak]


def main() -> int:
    parser = argparse.ArgumentParser(description="Red Gate adversarial gate")
    parser.add_argument("--base-url", required=True, help="Base URL of the deployed target")
    args = parser.parse_args()
    base_url = args.base_url.rstrip("/")

    print(f"== Red Gate :: attacking {base_url} ==\n")
    results = [fn(base_url) for fn in ATTACKS]

    broke = [a for a in results if a.broke_in]
    for a in results:
        mark = "BREACH" if a.broke_in else "held"
        print(f"[{mark:^6}] {a.ident}  {a.name}")
        print(f"          {a.detail}")

    print()
    if broke:
        print(f"GATE: FAIL - {len(broke)} attack(s) succeeded. Promotion blocked.")
        return 1
    print("GATE: PASS - red team could not break in. Safe to promote.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
