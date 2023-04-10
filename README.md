# funnybot
funny
## getting started
- install `poetry`: https://python-poetry.org/docs/
- add this to your ~/.bashrc or zshrc:
```
export PATH="/home/<username>/.local/bin:$PATH"
export PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring
```
- create `.env` in root folder and add `export DISCORD_TOKEN="<discord token>"`
- run `source .env`
- run `poetry install`
- run `poetry shell`
- cd to `oi_discord_bot` and run `python3 onlyimages.py`
