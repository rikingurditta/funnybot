from database import OIDatabase
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
import uvloop
from datetime import datetime

CMD_PREFIX = "="
STAR_THRESHOLD = 5
DEL_THRESHOLD = 5
CONFESSIONS_PER_DAY = 2
IMAGES_CHANNEL_NAME = "images"
OI_DB_BACKUP_COMMAND = (
    "scp -P 1337 oi.db remilia@10.88.111.37:/mnt/storage/oi_bak/{}.db".format(
        datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
    )
)
LOG_FILE_NAME = "oi.log"

OI_GUILD_ID = 961028480189992970
GENERAL_CHANNEL_ID = 1032482385205415947
IMAGES_CHANNEL_ID = 961028480189992973
HI_CHAT_ID = 1032482927394693178
BESTOF_CHANNEL_ID = 1075618133571809281
OI_DEV_ROLE_ID = 1081679547302420541
RIIN_ROLE_ID = 1035448479742427196
BOT_TEST_STUFF_CHANNEL_ID = 961029138129490032
CONFESSIONS_CHANNEL_ID = GENERAL_CHANNEL_ID
WYR_CHANNEL_ID = GENERAL_CHANNEL_ID
LATER_ROLE_ID = 1052688337745485824
OI_BOT_DEV_IDS = [
    277621798357696513,
    189215545206374400,
    690534844710649856,
    381994860523159562,
]


CUM_EMOJIS = ["💦", "🥵", "🤢", "🥛", "😋"]
CRY_EMOJIS = ["😢", "🫂", "😭", "😔", "☹️"]
CONFESS_EMOJIS = ["😳", "‼️", "⁉️", "💀", "😱"]
WYR_EMOJIS = ["🅰️", "🅱️"]
WYR_REACT_EMOJIS = ["🤔", "💭"]

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
db = OIDatabase()
