import signal
from typing import Any, Optional

import ffmpeg
from pyrogram import Client, filters
import pyrogram
from pyrogram.raw.types.update_dc_options import UpdateDcOptions
from pyrogram.types import Message
from pytgcalls import GroupCallFactory
from pyrogram.raw import functions, types
import sys
from config import ADMINS, API_HASH, API_ID, SESSION_NAME


CLIENT_TYPE = GroupCallFactory.MTPROTO_CLIENT_TYPE.PYROGRAM

async def admin_filter(_, __, m: Message):
    return m.from_user.id in ADMINS


admin = filters.create(admin_filter)

pyro_client = Client(
    f"sessions/{SESSION_NAME}",
    api_hash=API_HASH,
    api_id=API_ID,
)


GROUP_CALLS = {}
FFMPEG_PROCESSES = {}



if __name__ == '__main__':
    pyro_client.run()
