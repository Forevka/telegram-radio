import signal
from typing import Optional

import ffmpeg  # pip install ffmpeg-python
from pyrogram import Client, filters, idle
from pyrogram.types import Message
import asyncio
import os

from pytgcalls import GroupCallFactory, GroupCallFactory  # pip install pytgcalls[pyrogram]

LAST_RECORDED_DATA = None


def on_played_data(_, length: int) -> Optional[bytes]:
    return LAST_RECORDED_DATA


def on_recorded_data(_, data: bytes, length: int) -> None:
    global LAST_RECORDED_DATA
    LAST_RECORDED_DATA = data

pyro_client = Client(
    'pytgcalls',
    api_hash=os.environ.get('API_HASH', ''),
    api_id=os.environ.get('API_ID', 0),
)

async def main(client):
    # its for Pyrogram
    await client.start()
    while not client.is_connected:
        await asyncio.sleep(1)
    # for Telethon you can use this one:
    # client.start()

    group_call_factory = GroupCallFactory(client, CLIENT_TYPE)

    # handle input audio data from the first peer
    group_call_from = group_call_factory.get_raw_group_call(on_recorded_data=on_recorded_data)
    await group_call_from.start()

    # transfer input audio from the first peer to the second using handlers
    group_call_to = group_call_factory.get_raw_group_call(on_played_data=on_played_data)
    await group_call_to.start("@vaporwave_radio")




if __name__ == '__main__':
    asyncio.run(main(pyro_client))
    pyro_client.run()