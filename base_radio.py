import asyncio
from periodic_helper import Periodic
from typing import Any, Awaitable, Callable, Dict
import ffmpeg
from pyrogram.client import Client
from pytgcalls.group_call_factory import GroupCallFactory
import signal


def calc_input_filename(name: Any):
    return f'stations/radio-{name}.raw'


class BaseRadio:
    def __init__(self, url: str, group_id: int, factory: GroupCallFactory):
        self.url = url
        self.group_id = group_id
        self.group_call_factory: GroupCallFactory = factory
        self.radio_stream = factory.get_file_group_call(
            calc_input_filename(group_id)
        )

        self.ffmpeg_stream = (
            ffmpeg.input(url)
            .output(calc_input_filename(group_id), format='s16le', acodec='pcm_s16le', ac=2, ar='48k')
            .overwrite_output()
        )
        self.ffmpeg_process = None

        self.is_streaming = False

    async def stop(self,):
        self.ffmpeg_process.send_signal(signal.SIGTERM)
        await self.radio_stream.stop()

        self.is_streaming = False

    async def start(self,):
        self.ffmpeg_process = self.ffmpeg_stream.run_async()
        await self.radio_stream.start(self.group_id)

        self.is_streaming = True


class PeriodicFetchMetadataRadio(BaseRadio):
    def __init__(self, url: str, group_id: int, factory: GroupCallFactory, time_interval: int, metadata_callback: Awaitable):
        super().__init__(url, group_id, factory)

        self.time_interval = time_interval
        self.fetch_metadata = metadata_callback
        self._task = Periodic(time_interval, self.fetch_metadata, factory.client, group_id,)

    async def start(self):
        await super().start()
        await self._task.start()

class RadioHolder:
    def __init__(self,):
        self.radios: Dict[int, BaseRadio] = {}
        self.app: Client = None

    def add_radio(self, radio: BaseRadio):
        self.radios[radio.group_id] = radio

    def get_radio(self, group_id: int):
        return self.radios.get(group_id)

    def is_group_have_radio(self, group_id: int):
        return group_id in self.radios


radio_holder = RadioHolder()
