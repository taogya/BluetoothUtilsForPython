
import asyncio
import logging
import os

import bleak as blk
from asgiref.sync import sync_to_async

from django.core.management import BaseCommand
from django.core.management.base import CommandParser
from django.db import connection
from django_bleak.models import BleScanEvent, BleScanFilter

logger = logging.getLogger('ble_scanner')


class Command(BaseCommand):

    async def callback(self, dev: blk.BLEDevice, adv: blk.AdvertisementData):
        await sync_to_async(BleScanFilter.objects.filter(is_enabled=True).order_by('id').create_data)([(dev, adv)])

    async def scan_task(self, async_event: asyncio.Event):
        async with blk.BleakScanner(self.callback):
            logger.info('scan_task wait until set async event.')
            await async_event.wait()
        logger.info('scan_task finish.')

    async def monitor_task(self, async_event: asyncio.Event, name: str, interval: float):
        event = await sync_to_async(BleScanEvent.objects.get)(name=name)
        while event.interval > 0.0:
            logger.info(f'{event}')
            await asyncio.sleep(interval)
            if not event.is_enabled:
                async_event.set()
                logger.info('set async event.')
                break
            event = await sync_to_async(BleScanEvent.objects.get)(name=name)
        logger.info('monitor_task finish.')

    def add_arguments(self, parser: CommandParser):
        parser.add_argument('event', help='scan event name.', type=str)

    def main(self, event, *args, **options):
        # get scan event. if does not exists it, create.
        scan_event, _ = BleScanEvent.objects.get_or_create(name=event)
        if scan_event.pid is not None:
            err_msg = f'{scan_event.name} is already operating. pid = {scan_event.pid}.'
            logger.error(f'{err_msg}')
            raise Exception(f'{err_msg}')
        # update scan event.
        scan_event.is_enabled = True
        scan_event.pid = os.getpid()
        scan_event.save()
        logger.info(f'updated scan event. -> {scan_event}')
        # do task.
        async_event = asyncio.Event()
        loop = asyncio.get_event_loop()
        futures = asyncio.gather(self.scan_task(async_event),
                                 self.monitor_task(async_event, scan_event.name, scan_event.interval))
        try:
            loop.run_until_complete(futures)
            logger.info('loop finish.')
        except BaseException:
            logger.exception('internal error.')
        finally:
            scan_event = BleScanEvent.objects.get(name=event)
            scan_event.is_enabled = False
            scan_event.pid = None
            scan_event.save()
            logger.info(f'updated scan event. -> {scan_event}')

    def handle(self, event, *args, **options):
        pid = os.fork()
        if pid == 0:
            logger.info('start ble_scanner')
            connection.close()
            self.main(event, *args, **options)
            logger.info('end ble_scanner')
            exit(0)
