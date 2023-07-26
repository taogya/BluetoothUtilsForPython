
import asyncio
import logging
import time

import bleak as blk
import psutil
from asgiref.sync import sync_to_async

from django.core.management import BaseCommand
from django.core.management.base import CommandParser
from django_bleak.models import BleScanEvent, BleScanFilter

logger = logging.getLogger('ble_scanner')


class Command(BaseCommand):

    filters = BleScanFilter.objects.filter(is_enabled=True).order_by('id')

    async def callback(self, dev: blk.BLEDevice, adv: blk.AdvertisementData):
        ret = await sync_to_async(self.filters.create_data)([(dev, adv)])
        if len(ret):
            logger.debug(f'create -> {ret}')

    async def scan_task(self, async_event: asyncio.Event):
        async with blk.BleakScanner(self.callback):
            logger.info('scan_task wait until set async event.')
            await async_event.wait()
        logger.info('scan_task finish.')

    async def monitor_task(self, async_event: asyncio.Event, name: str, interval: float):
        event = await sync_to_async(BleScanEvent.objects.get)(name=name)
        try:
            while event.interval > 0.0:
                logger.debug(f'{event}')
                time.sleep(event.interval)
                if not event.is_enabled:
                    logger.info('is_enabled switched to false.')
                    break
                event = await sync_to_async(BleScanEvent.objects.get)(name=name)
                self.filters = await sync_to_async(BleScanFilter.objects.filter)(is_enabled=True)
        finally:
            async_event.set()
            logger.info('set async event.')
            logger.info('monitor_task finish.')

    def add_arguments(self, parser: CommandParser):
        parser.add_argument('event', help='scan event name.', type=str)
        parser.add_argument('--debug', help='debug flag.', action='store_true')

    def get_scan_event(self, event):
        # get scan event. if does not exists it, create.
        scan_event, _ = BleScanEvent.objects.get_or_create(name=event)
        logger.info(f'{scan_event} -> {scan_event.status}')
        if scan_event.status in (BleScanEvent.Status.RUNNING, BleScanEvent.Status.ZOMBIE):
            psutil.Process(scan_event.pid).kill()
            logger.info(f'{scan_event.pid} killed')
        # update scan event.
        proc = psutil.Process()
        scan_event.is_enabled = True
        scan_event.pid = proc.pid
        scan_event.create_time = proc.create_time()
        scan_event.save()
        logger.info(f'updated scan event. -> {scan_event}')
        return scan_event

    def main(self, event, interval, *args, **options):
        logger.info('start ble_scanner')
        try:
            # do task.
            async_event = asyncio.Event()
            loop = asyncio.get_event_loop()
            futures = asyncio.gather(self.scan_task(async_event),
                                     self.monitor_task(async_event, event, interval))
            loop.run_until_complete(futures)
            logger.info('loop finish.')
        except BaseException:
            logger.exception('internal error.')
        finally:
            scan_event = BleScanEvent.objects.filter(name=event).first()
            if scan_event:
                scan_event.is_enabled = False
                scan_event.pid = None
                scan_event.create_time = None
                scan_event.save()
                logger.info(f'updated scan event. -> {scan_event}')
            logger.info('end ble_scanner')

    def handle(self, event, *args, **options):
        scan_event = self.get_scan_event(event)
        self.main(scan_event.name, scan_event.interval, *args, **options)
