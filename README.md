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
## contributing
- use the logging library
- in new files add the following lines:
```
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(" "message)s",
    handlers=[
            logging.FileHandler("oi.log"),
            logging.StreamHandler()
        ]
)
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
```
- use `log.info`, `log.error`, `log.warning` etc
- format with https://github.com/psf/black
- use the cogs system by following existing code in the cogs folder
