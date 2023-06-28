
import asyncio
import logging

import bleak as blk
from asgiref.sync import sync_to_async

from django_bleak.management.commands.ble_scanner import Command as BleCommand
from django_bleak.models import BleScanEvent, BleScanFilter

logger = logging.getLogger('ble_scanner')


class Command(BleCommand):

    async def callback(self, dev: blk.BLEDevice, adv: blk.AdvertisementData):
        pass

    async def scan_task(self, async_event: asyncio.Event):
        logger.info('pass scan_task. instead doing in monitor_task.')

    async def monitor_task(self, async_event: asyncio.Event, name: str, interval: float):
        event = await sync_to_async(BleScanEvent.objects.get)(name=name)
        try:
            while event.interval > 0.0:
                logger.debug(f'{event}')
                if not event.is_enabled:
                    logger.info('is_enabled switched to false.')
                    break
                scan_res = await blk.BleakScanner.discover(timeout=event.interval, return_adv=True)
                ret = await sync_to_async(self.filters.create_data)(scan_res.values())
                if len(ret):
                    logger.debug(f'create -> {ret}')
                event = await sync_to_async(BleScanEvent.objects.get)(name=name)
                self.filters = await sync_to_async(BleScanFilter.objects.filter)(is_enabled=True)
        finally:
            async_event.set()
            logger.info('set async event.')
            logger.info('monitor_task finish.')
