# Tiny Chess runner candidate

`main.py` is a deterministic Python 3 standard-library agent. It uses only `MAKEFUN_ENV_URL`: POST `/game` with `{}`, then POST `/move` with `{"game": n, "move": "<uci>"}` until the env says `done`. It makes no model calls, reads no repository files, and disables proxy use. Its picker selects only from the env-provided legal moves.

Run mock-only checks: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_main.py`. The test replaces the HTTP opener; it does not contact a server. Official local grading was not run: the current Python 3.13 grade path requires Docker, which was not used.
