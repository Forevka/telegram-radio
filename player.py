import signal

import ffmpeg  # pip install ffmpeg-python
from pyrogram import Client, filters, idle
from pyrogram.types import Message
import asyncio
import os

from pytgcalls import GroupCallFactory, GroupCallFactory  # pip install pytgcalls[pyrogram]


pyro_client = Client(
    'pytgcalls',
    api_hash=os.environ.get('API_HASH', ''),
    api_id=os.environ.get('API_ID', 0),
)

main_filter = filters.text & filters.outgoing & ~filters.edited
cmd_filter = lambda cmd: filters.command(cmd, prefixes='!')

group_call = None


def init_client_and_delete_message(func):
    async def wrapper(client, message):
        global group_call
        if not group_call:
            group_call = GroupCallFactory(client).get_file_group_call()

        await message.delete()

        return await func(client, message)

    return wrapper


@pyro_client.on_message(main_filter & cmd_filter('play'))
async def start_playout(_, message: Message):
    if not message.reply_to_message or not message.reply_to_message.audio:
        return await message.delete()

    if not group_call:
        return await message.reply_text('You are not joined (type /join)')

    input_filename = 'input.raw'

    status = '- Downloading... \n'
    await message.edit_text(status)
    audio_original = await message.reply_to_message.download()

    status += '- Converting... \n'

    ffmpeg.input(audio_original).output(
        input_filename, format='s16le', acodec='pcm_s16le', ac=2, ar='48k'
    ).overwrite_output().run()

    os.remove(audio_original)

    status += f'- Playing **{message.reply_to_message.audio.title}**...'
    await message.edit_text(status)

    group_call.input_filename = input_filename


@pyro_client.on_message(main_filter & cmd_filter('volume'))
@init_client_and_delete_message
async def volume(_, message):
    if len(message.command) < 2:
        return await message.reply_text('You forgot to pass volume (1-200)')

    await group_call.set_my_volume(message.command[1])


@pyro_client.on_message(main_filter & cmd_filter('join'))
@init_client_and_delete_message
async def start(_, message: Message):
    await group_call.start(message.chat.id)


@pyro_client.on_message(main_filter & cmd_filter('leave'))
@init_client_and_delete_message
async def stop(*_):
    await group_call.stop()


@pyro_client.on_message(main_filter & cmd_filter('rejoin'))
@init_client_and_delete_message
async def reconnect(*_):
    await group_call.reconnect()


@pyro_client.on_message(main_filter & cmd_filter('replay'))
@init_client_and_delete_message
async def restart_playout(*_):
    group_call.restart_playout()


@pyro_client.on_message(main_filter & cmd_filter('stop'))
@init_client_and_delete_message
async def stop_playout(*_):
    group_call.stop_playout()


@pyro_client.on_message(main_filter & cmd_filter('mute'))
@init_client_and_delete_message
async def mute(*_):
    group_call.set_is_mute(True)


@pyro_client.on_message(main_filter & cmd_filter('unmute'))
@init_client_and_delete_message
async def unmute(*_):
    group_call.set_is_mute(False)


@pyro_client.on_message(main_filter & cmd_filter('pause'))
@init_client_and_delete_message
async def pause(*_):
    group_call.pause_playout()


@pyro_client.on_message(main_filter & cmd_filter('resume'))
@init_client_and_delete_message
async def resume(*_):
    group_call.resume_playout()

if __name__ == '__main__':
    pyro_client.run()