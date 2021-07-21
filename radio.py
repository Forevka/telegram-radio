import signal

import ffmpeg
from pyrogram import Client, filters
import pyrogram
from pyrogram.types import Message
from pytgcalls import GroupCallFactory
from pyrogram.raw import functions

from config import ADMINS, API_HASH, API_ID, SESSION_NAME

CLIENT_TYPE = GroupCallFactory.MTPROTO_CLIENT_TYPE.PYROGRAM

pyro_client = Client(
    f"sessions/{SESSION_NAME}",
    api_hash=API_HASH,
    api_id=API_ID,
)


async def admin_filter(_, __, m: Message):
    return m.from_user.id in ADMINS


admin = filters.create(admin_filter)

GROUP_CALLS = {}
FFMPEG_PROCESSES = {}


@pyro_client.on_message(admin & filters.command('dc', prefixes='!'))
async def get_dc(client: Client, message: Message):
    await message.reply_text(f'dc {await client.storage.dc_id()}')


@pyro_client.on_message(admin & filters.command('start', prefixes='!'))
async def start(client, message: Message):
    if len(message.command) < 3:
        await message.reply_text('!start @group_username https://link-to-stream/')
        return

    group = None
    try:
        group = await pyro_client.get_chat(message.command[1].replace('@', ''))
    except pyrogram.errors.exceptions.bad_request_400.UsernameInvalid:
        await message.reply_text(f'can''t resolve this username')


    group_id = group.id

    input_filename = f'stations/radio-{group_id}.raw'

    group_call = GROUP_CALLS.get(group_id)
    if group_call is None:
        group_call = GroupCallFactory(
            client, path_to_log_file='').get_file_group_call(input_filename)
        GROUP_CALLS[group_id] = group_call

    process = FFMPEG_PROCESSES.get(group_id)
    if process:
        process.send_signal(signal.SIGTERM)

    station_stream_url = message.command[2].strip()

    await group_call.start(group_id)

    process = (
        ffmpeg.input(station_stream_url)
        .output(input_filename, format='s16le', acodec='pcm_s16le', ac=2, ar='48k')
        .overwrite_output()
        .run_async()
    )
    FFMPEG_PROCESSES[group_id] = process

    await message.reply_text(f'Radio for {group_id} with {station_stream_url} is playing...')


@pyro_client.on_message(admin & filters.command('stop', prefixes='!'))
async def stop(_, message: Message):
    if len(message.command) < 2:
        await message.reply_text('!stop @group_username')
        return

    group = None
    try:
        group = await pyro_client.get_chat(message.command[1].replace('@', ''))
    except pyrogram.errors.exceptions.bad_request_400.UsernameInvalid:
        await message.reply_text(f'can''t resolve this username')

    group_id = group.id

    group_call = GROUP_CALLS.get(group_id)
    if group_call:
        await group_call.stop()

    process = FFMPEG_PROCESSES.get(group_id)
    if process:
        process.send_signal(signal.SIGTERM)


if __name__ == '__main__':
    pyro_client.run()
