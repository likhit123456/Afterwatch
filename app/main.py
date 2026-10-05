"""
Red Gate demo target app (FastAPI).

This app ships INTENTIONALLY VULNERABLE as the baseline state. It is a training
target for the Red Gate pipeline: CI scanners + the red-team gate detect these
issues, and the defender agent patches them. The three planted issues are:

  VULN-1  SQL injection in /login  (string-formatted query)
  VULN-2  Missing authorization on /admin/users  (no auth check)
  VULN-3  Hardcoded secret in source  (API_KEY below)

Each is tagged with a `# noqa: REDGATE-VULN-n` marker so the demo can point at
the exact lines. Do not use any of this in production.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .db import get_conn, init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Red Gate Target", version="0.1.0", lifespan=lifespan)

# VULN-3: hardcoded secret committed to source control. Secret Detection should
# flag this; the defender agent moves it to an env var.
API_KEY = "sk-live-9f8e7d6c5b4a3210redgatedemo"  # noqa: REDGATE-VULN-3


class LoginReq(BaseModel):
    username: str
    password: str


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "red-gate-target"}


@app.post("/login")
def login(req: LoginReq) -> dict:
    # VULN-1: user input is concatenated straight into SQL. A payload like
    # password = "' OR '1'='1" authenticates as any user.
    conn = get_conn()
    query = (
        "SELECT id, username, role FROM users "
        f"WHERE username = '{req.username}' AND password = '{req.password}'"  # noqa: REDGATE-VULN-1
    )
    row = conn.execute(query).fetchone()
    conn.close()
    if row is None:
        raise HTTPException(status_code=401, detail="invalid credentials")
    return {"id": row["id"], "username": row["username"], "role": row["role"]}


@app.get("/admin/users")
def list_users() -> dict:
    # VULN-2: no authentication/authorization. Any caller can dump every user,
    # including password hashes and the admin account.
    conn = get_conn()
    rows = conn.execute("SELECT id, username, role, password FROM users").fetchall()
    conn.close()
    return {"users": [dict(r) for r in rows]}  # noqa: REDGATE-VULN-2
