
import asyncio
import logging

import bleak as blk
from asgiref.sync import sync_to_async
from django.core.management import BaseCommand
from django.core.management.base import CommandParser

from django_bleak.models import BleScanEvent, BleScanFilter

logger = logging.getLogger('ble_scanner')


class Command(BaseCommand):

    async def callback(self, dev: blk.BLEDevice, adv: blk.AdvertisementData):
        await sync_to_async(BleScanFilter.objects.filter(is_enabled=True).order_by('id').create_data)([(dev, adv)])

    async def scan_task(self, async_event: asyncio.Event):
        async with blk.BleakScanner(self.callback):
            await async_event.wait()

    async def monitor_task(self, async_event: asyncio.Event, name: str, interval: float):
        while True:
            await asyncio.sleep(interval)
            event = await sync_to_async(BleScanEvent.objects.get)(name=name)
            if not event.is_enabled:
                async_event.set()
                return

    def add_arguments(self, parser: CommandParser):
        parser.add_argument('event', help='scan event name.', type=str)
        parser.add_argument('--interval', help='event check interval[sec].', nargs='?', type=float)

    def handle(self, event, *args, **options):
        # get scan event. if does not exists it, create.
        scan_event, _ = BleScanEvent.objects.get_or_create(name=event)
        scan_event.is_enabled = True
        scan_event.interval = options.pop('interval') or BleScanEvent.DEFAULT_INTERVAL
        scan_event.save()
        # do task.
        async_event = asyncio.Event()
        loop = asyncio.get_event_loop()
        futures: asyncio.Future = \
            asyncio.gather(self.scan_task(async_event),
                           self.monitor_task(async_event, scan_event.name, scan_event.interval))
        loop.run_until_complete(futures)
        return futures.result()
