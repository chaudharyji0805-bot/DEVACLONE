from pyrogram import filters
from pyrogram.types import Message

from VIP_DEVA import app
from VIP_DEVA.core.call import DEVA

welcome = 20
close = 30


@app.on_message(filters.video_chat_started, group=welcome)
@app.on_message(filters.video_chat_ended, group=close)
async def welcome(_, message: Message):
    await DEVA.stop_stream_force(message.chat.id)
