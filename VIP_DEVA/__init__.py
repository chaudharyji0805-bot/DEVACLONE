from VIP_DEVA.core.bot import DEVA
from VIP_DEVA.core.dir import dirr
from VIP_DEVA.core.git import git
from VIP_DEVA.core.userbot import Userbot
from VIP_DEVA.misc import dbb, heroku
from pyrogram import Client
from SafoneAPI import SafoneAPI
from .logging import LOGGER

dirr()

# ✅ Heroku/hosted pe by default OFF
import os
if os.getenv("AUTO_GIT_UPDATE", "false").lower() in ("1", "true", "yes"):
    git()
else:
    LOGGER(__name__).info("AUTO_GIT_UPDATE disabled, skipping git updater.")

dbb()
heroku()

app = DEVA()
api = SafoneAPI()
userbot = Userbot()

from .platforms import *

Apple = AppleAPI()
Carbon = CarbonAPI()
SoundCloud = SoundAPI()
Spotify = SpotifyAPI()
Resso = RessoAPI()
Telegram = TeleAPI()
YouTube = YouTubeAPI()

