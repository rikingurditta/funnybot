from database import OIDatabase
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
import uvloop

CMD_PREFIX = "="
STAR_THRESHOLD = 5
DEL_THRESHOLD = 5
IMAGES_CHANNEL_NAME = "images"

OI_GUILD_ID = 961028480189992970
GENERAL_CHANNEL_ID = 1032482385205415947
HI_CHAT_ID = 1032482927394693178
BESTOF_CHANNEL_ID = 1075618133571809281
OI_DEV_ROLE_ID = 1081679547302420541
RIIN_ROLE_ID = 1035448479742427196
BOT_TEST_STUFF_CHANNEL_ID = 961029138129490032
CONFESSIONS_CHANNEL_ID = GENERAL_CHANNEL_ID
WYR_CHANNEL_ID = GENERAL_CHANNEL_ID
LATER_ROLE_ID = 1052688337745485824


CUM_EMOJIS = ["💦", "🥵", "🤢", "🥛", "😋"]
CRY_EMOJIS = ["😢", "🫂", "😭", "😔", "☹️"]
CONFESS_EMOJIS = ["😳", "‼️", "⁉️", "💀", "😱"]
WYR_EMOJIS = ["🅰️", "🅱️"]
WYR_REACT_EMOJIS = ["🤔", "💭"]

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
global_event_loop = asyncio.get_event_loop()
scheduler = AsyncIOScheduler(global_event_loop)
db = OIDatabase()
