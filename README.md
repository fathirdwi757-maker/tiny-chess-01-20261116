# Tiny Chess runner candidate

[![make.fun · tiny-chess-01](https://make.fun/badge/tiny-chess-01.svg)](https://make.fun/bounty/tiny-chess-01?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)
[![rank](https://make.fun/badge/tiny-chess-01/fathirdwi757-maker/tiny-chess-01-20261116/rank.svg)](https://make.fun/bounty/tiny-chess-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)
[![reward](https://make.fun/badge/tiny-chess-01/fathirdwi757-maker/tiny-chess-01-20261116/reward.svg)](https://make.fun/bounty/tiny-chess-01?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)

`main.py` is a deterministic Python 3 standard-library agent. It uses only `MAKEFUN_ENV_URL`: POST `/game` with `{}`, then POST `/move` with `{"game": n, "move": "<uci>"}` until the env says `done`. It makes no model calls, reads no repository files, and disables proxy use. Its picker selects only from the env-provided legal moves. See the [Make.fun Tiny Chess bounty](https://make.fun/bounty/tiny-chess-01).

Run mock-only checks: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_main.py`. The test replaces the HTTP opener; it does not contact a server. Official local grading was not run: the current Python 3.13 grade path requires Docker, which was not used.
