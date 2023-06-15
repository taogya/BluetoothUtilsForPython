
from contextlib import ExitStack
from unittest.mock import patch

import bleak as blk

from django.test import TestCase
from django_bleak.models.scanner import (BleScanDevice, BleScanResult,
                                         CustomQueryset)


class MockModel:

    def __init__(self, is_match):
        self.__is_match = is_match

    def is_match(self, data):
        return self.__is_match


class Test(TestCase):

    def setUp(self) -> None:
        self.stack = ExitStack()
        return super().setUp()

    def tearDown(self) -> None:
        self.stack.close()
        return super().tearDown()

    def test_data_list_empty(self):
        self.stack.enter_context(
            patch(
                'django_bleak.models.scanner.CustomQueryset.__iter__',
                return_value=iter([MockModel(False)])
            )
        )
        CustomQueryset().create_data([])

        self.assertEqual(BleScanDevice.objects.count(), 0)
        self.assertEqual(BleScanResult.objects.count(), 0)

    def test_filter_data_empty(self):
        dev = blk.BLEDevice(
            '12:34:56:78:90:AB',
            'dev-001',
            None,
            -50
        )
        adv = blk.AdvertisementData(
            'dev-001',
            {0xffff: b'manufacturer data'},
            {'01234567-0123-0123-0123-0123456789AB': b'service data'},
            ['01234567-0123-0123-0123-0123456789AB'],
            0,
            -50,
            tuple()
        )
        self.stack.enter_context(
            patch(
                'django_bleak.models.scanner.CustomQueryset.__iter__',
                return_value=iter([MockModel(False)])
            )
        )
        CustomQueryset().create_data([(dev, adv)])

        self.assertEqual(BleScanDevice.objects.count(), 0)
        self.assertEqual(BleScanResult.objects.count(), 0)

    def test_only_manufacturer_data(self):
        dev = blk.BLEDevice(
            '12:34:56:78:90:AB',
            'dev-001',
            None,
            -50
        )
        adv = blk.AdvertisementData(
            'dev-001',
            {0xffff: b'manufacturer data'},
            {},
            [],
            0,
            -50,
            tuple()
        )
        self.stack.enter_context(
            patch(
                'django_bleak.models.scanner.CustomQueryset.__iter__',
                return_value=iter([MockModel(True)])
            )
        )
        CustomQueryset().create_data([(dev, adv)])

        self.assertEqual(BleScanDevice.objects.count(), 1)
        self.assertEqual(BleScanResult.objects.count(), 1)
        self.assertIsNotNone(BleScanDevice.objects
                             .get(mac_addr='12:34:56:78:90:AB'))
        self.assertIsNotNone(BleScanResult.objects
                             .get(device_id='12:34:56:78:90:AB',
                                  local_name='dev-001',
                                  company_code=0xffff,
                                  manufacturer_data=b'manufacturer data',
                                  service_uuid__isnull=True,
                                  service_data__isnull=True,
                                  tx_power=0,
                                  rssi=-50))

    def test_only_service_data(self):
        dev = blk.BLEDevice(
            '12:34:56:78:90:AB',
            'dev-001',
            None,
            -50
        )
        adv = blk.AdvertisementData(
            'dev-001',
            {},
            {'01234567-0123-0123-0123-0123456789AB': b'service data'},
            ['01234567-0123-0123-0123-0123456789AB'],
            0,
            -50,
            tuple()
        )
        self.stack.enter_context(
            patch(
                'django_bleak.models.scanner.CustomQueryset.__iter__',
                return_value=iter([MockModel(True)])
            )
        )
        CustomQueryset().create_data([(dev, adv)])

        self.assertEqual(BleScanDevice.objects.count(), 1)
        self.assertEqual(BleScanResult.objects.count(), 1)
        self.assertIsNotNone(BleScanDevice.objects
                             .get(mac_addr='12:34:56:78:90:AB'))
        self.assertIsNotNone(BleScanResult.objects
                             .get(device_id='12:34:56:78:90:AB',
                                  local_name='dev-001',
                                  company_code__isnull=True,
                                  manufacturer_data__isnull=True,
                                  service_uuid='01234567-0123-0123-0123-0123456789AB',
                                  service_data=b'service data',
                                  tx_power=0,
                                  rssi=-50))

    def test_both(self):
        dev = blk.BLEDevice(
            '12:34:56:78:90:AB',
            'dev-001',
            None,
            -50
        )
        adv = blk.AdvertisementData(
            'dev-001',
            {0xffff: b'manufacturer data'},
            {'01234567-0123-0123-0123-0123456789AB': b'service data'},
            ['01234567-0123-0123-0123-0123456789AB'],
            0,
            -50,
            tuple()
        )
        self.stack.enter_context(
            patch(
                'django_bleak.models.scanner.CustomQueryset.__iter__',
                return_value=iter([MockModel(True)])
            )
        )
        CustomQueryset().create_data([(dev, adv)])

        self.assertEqual(BleScanDevice.objects.count(), 1)
        self.assertEqual(BleScanResult.objects.count(), 2)
        self.assertIsNotNone(BleScanDevice.objects
                             .get(mac_addr='12:34:56:78:90:AB'))
        self.assertIsNotNone(BleScanResult.objects
                             .get(device_id='12:34:56:78:90:AB',
                                  local_name='dev-001',
                                  company_code=0xffff,
                                  manufacturer_data=b'manufacturer data',
                                  service_uuid__isnull=True,
                                  service_data__isnull=True,
                                  tx_power=0,
                                  rssi=-50))
        self.assertIsNotNone(BleScanResult.objects
                             .get(device_id='12:34:56:78:90:AB',
                                  local_name='dev-001',
                                  company_code__isnull=True,
                                  manufacturer_data__isnull=True,
                                  service_uuid='01234567-0123-0123-0123-0123456789AB',
                                  service_data=b'service data',
                                  tx_power=0,
                                  rssi=-50))

    def test_already_exists_blescandevice(self):
        BleScanDevice.objects.create(mac_addr='12:34:56:78:90:AB')
        dev = blk.BLEDevice(
            '12:34:56:78:90:AB',
            'dev-001',
            None,
            -50
        )
        adv = blk.AdvertisementData(
            'dev-001',
            {0xffff: b'manufacturer data'},
            {'01234567-0123-0123-0123-0123456789AB': b'service data'},
            ['01234567-0123-0123-0123-0123456789AB'],
            0,
            -50,
            tuple()
        )
        self.stack.enter_context(
            patch(
                'django_bleak.models.scanner.CustomQueryset.__iter__',
                return_value=iter([MockModel(True)])
            )
        )
        CustomQueryset().create_data([(dev, adv)])

        self.assertEqual(BleScanDevice.objects.count(), 1)
