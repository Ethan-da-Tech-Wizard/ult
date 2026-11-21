# Security policy

## Reporting a vulnerability

Please report security problems privately, not in a public issue.

Use GitHub's private vulnerability reporting: on this repository open the **Security** tab and choose
**Report a vulnerability**. Note for the maintainer: this feature must be switched on in the repository's
settings UI (Settings, Code security, Private vulnerability reporting); until it is, that button will not
exist, and this file does not claim it is enabled.

Please include the version or commit, what you did, and what you expected versus saw. This is a hobby
educational project: expect a reply when the maintainer can, not an SLA.

## Scope

- In scope: the local server in `server/`, the browser client in `client/`, the sandbox runner and the Docker
  image definition, the CI workflows.
- Known and documented, not vulnerabilities: running with `ULT_ALLOW_HOST_EXEC=1` or `ZEUS_ALLOW_HOST_SHELL=1`
  (explicit opt-ins that run code on your computer), another local program running as the same user, and
  container escapes that rely on a host kernel or Docker bug. See "Security model" in the README.

## Supported versions

Only the latest commit on `main`.
