import aiohttp
from pyrogram.client import Client
from pyrogram.raw.functions.channels.get_full_channel import GetFullChannel
from pyrogram.raw.functions.phone.edit_group_call_title import EditGroupCallTitle
from models.plaza_metadata_model import plaza_metadata_from_dict

async def fetch_plaza_metadata(client: Client, group_id: int):
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api-beta2.plaza.one/status') as resp:
            data = plaza_metadata_from_dict(await resp.json())
            
            peer = await client.resolve_peer(group_id)
            chat = await client.send(GetFullChannel(channel=peer))
            data = EditGroupCallTitle(call=chat.full_chat.call, title=f"{data.song.artist} - {data.song.title}")
            await client.send(data)