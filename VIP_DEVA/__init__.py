from VIP_DEVA.core.bot import DEVA
from VIP_DEVA.core.dir import dirr
from VIP_DEVA.core.git import git
from VIP_DEVA.core.userbot import Userbot
from VIP_DEVA.misc import dbb, heroku
from pyrogram import Client
from SafoneAPI import SafoneAPI
from .logging import LOGGER

dirr()
git()
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
