<!-- Paste everything below the line into a new GitLab issue. Title goes in the title field. -->

**Title:** Add a password reset endpoint

---

## Summary

Users who forget their password currently have no way to recover their account.
Add a password reset flow to the API.

## Requirements

- `POST /password-reset/request` accepts `{"username": "<name>"}` and returns
  `202 Accepted` whether or not the user exists (do not reveal which usernames
  are registered). It generates a single-use reset token that expires after 15
  minutes and stores it server-side.
- `POST /password-reset/confirm` accepts `{"username", "token", "new_password"}`.
  A valid, unexpired token updates the password and is consumed; anything else
  returns `400`.
- The token is delivered out of band. For now, log it server-side in place of an
  email provider.

## Acceptance criteria

- [ ] Both endpoints exist and are covered by tests in `tests/`.
- [ ] Existing tests (`/health`, `/login`) still pass.
- [ ] A reset token cannot be reused and cannot be used after it expires.
- [ ] Nothing in the responses reveals whether a username exists.
- [ ] The merge request passes the full Red Gate pipeline, including the
      red-team gate, before it is promoted.

## Notes

Keep the change small and focused. Any security findings raised by CI on the
resulting merge request should be fixed in that same merge request.
