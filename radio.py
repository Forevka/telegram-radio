from plaza_metadata import fetch_plaza_metadata
from base_radio import BaseRadio, PeriodicFetchMetadataRadio, radio_holder
import signal

import ffmpeg
from pyrogram import Client, filters
import pyrogram
from pyrogram.types import Message
from pytgcalls import GroupCallFactory
from pyrogram.raw.functions.channels import GetFullChannel
from pyrogram.raw.functions.phone import EditGroupCallTitle

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


@pyro_client.on_message(admin & filters.command('dc', prefixes='!'))
async def get_dc(client: Client, message: Message):
    await message.reply_text(f'dc {await client.storage.dc_id()}')


@pyro_client.on_message(admin & filters.command('ct', prefixes='!'))
async def change_name(client, message: Message):
    if len(message.command) < 3:
        await message.reply_text('!ct @group_username name')
        return

    peer = await client.resolve_peer(message.command[1].replace('@', ''))
    chat = await client.send(GetFullChannel(channel=peer))
    data = EditGroupCallTitle(call=chat.full_chat.call, title=message.command[2])
    await client.send(data)

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

    stream_url = message.command[2].strip()

    group_radio = radio_holder.get_radio(group.id)
    if group_radio is None or not group_radio.is_streaming:
        if ('plaza.one' in stream_url):
            group_radio = PeriodicFetchMetadataRadio(
                stream_url, 
                group.id, 
                GroupCallFactory(
                    client, 
                    path_to_log_file=''
                ),
                5,
                fetch_plaza_metadata,
            )
        else:
            group_radio = BaseRadio(
                stream_url, 
                group.id, 
                GroupCallFactory(
                    client, 
                    path_to_log_file=''
                )
            )

        radio_holder.add_radio(group_radio)

    if (group_radio.is_streaming):
        await message.reply_text(f'Radio for {group.id} already playing')
        return

    await group_radio.start()

    await message.reply_text(f'Radio for {group.id} with {group_radio.url} is playing...')


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

    group_radio = radio_holder.get_radio(group.id)
    if group_radio is None or not group_radio.is_streaming:
        await message.reply_text(f'Radio for {group.id} are not playing.')
        return
    
    await group_radio.stop()
    await message.reply_text(f'Radio for {group.id} stopped')



if __name__ == '__main__':
    pyro_client.run()
