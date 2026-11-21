# Contributing

Thanks for helping. This is a small educational game; keep changes small and tested.

1. Fork, branch, and open a pull request against `main`.
2. Run the tests before pushing (standard library and Node only, no Docker needed):

   ```
   for t in tests/test_*.py; do python3 "$t"; done
   for t in tests/test_*.js; do node "$t"; done
   node --check client/app.js
   ```

3. A bug fix needs a test that fails without the fix. Put it in `tests/` as `test_<topic>.py` or `.js`; both
   are picked up by CI automatically. Tests must not need fastapi, numpy, Docker or the network (see
   `tests/test_shell_guard.py` for the stand-in module pattern).
4. Never make player code run on the host by default, never add third-party network requests to the client,
   and escape any non-constant text before it goes into `innerHTML` (`escapeDiagnosticText`).
5. No secrets, personal emails or machine paths in commits.
6. Security issues: follow [SECURITY.md](SECURITY.md) instead of opening a public issue.

By contributing you agree your work is released under the MIT licence in [LICENSE](LICENSE).
