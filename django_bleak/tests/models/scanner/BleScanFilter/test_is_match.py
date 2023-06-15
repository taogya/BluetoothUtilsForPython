
import bleak as blk

from django.test import TestCase
from django_bleak.models.scanner import BleScanFilter


class Test(TestCase):

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

    @classmethod
    def setUpTestData(cls) -> None:
        cls.filter: BleScanFilter = BleScanFilter.objects\
            .create(mac_addr='12:34:56:78:90:AB',
                    local_name='dev-001',
                    company_code=0xffff,
                    manufacturer_data='^6d616e7566616374757265722064617461$',
                    service_uuid='01234567-0123-0123-0123-0123456789AB',
                    service_data='^736572766963652064617461$')
        return super().setUpTestData()

    def test_true_all_pass(self):
        ret = self.filter.is_match((self.dev, self.adv))

        self.assertTrue(ret)

    def test_false_mac_addr(self):
        self.filter.mac_addr = 'FF:FF:FF:FF:FF:FF'
        ret = self.filter.is_match((self.dev, self.adv))

        self.assertFalse(ret)

    def test_false_local_name(self):
        self.filter.local_name = 'dev-002'
        ret = self.filter.is_match((self.dev, self.adv))

        self.assertFalse(ret)

    def test_false_company_code(self):
        self.filter.company_code = 0x0000
        ret = self.filter.is_match((self.dev, self.adv))

        self.assertFalse(ret)

    def test_false_manufacturer_data(self):
        self.filter.manufacturer_data = r'^6d616e75666163747572657220646174$'
        ret = self.filter.is_match((self.dev, self.adv))

        self.assertFalse(ret)

    def test_false_service_uuid(self):
        self.filter.service_uuid = 'ffffffff-ffff-ffff-ffff-ffffffffffff'
        ret = self.filter.is_match((self.dev, self.adv))

        self.assertFalse(ret)

    def test_false_service_data(self):
        self.filter.service_data = r'^7365727669636520646174$'
        ret = self.filter.is_match((self.dev, self.adv))

        self.assertFalse(ret)

    def test_flase_rssi_max(self):
        self.filter.rssi_max = -51
        ret = self.filter.is_match((self.dev, self.adv))

        self.assertFalse(ret)

    def test_true_rssi_max(self):
        self.filter.rssi_max = -50
        ret = self.filter.is_match((self.dev, self.adv))

        self.assertTrue(ret)

    def test_true_rssi_min(self):
        self.filter.rssi_min = -50
        ret = self.filter.is_match((self.dev, self.adv))

        self.assertTrue(ret)

    def test_flase_rssi_min(self):
        self.filter.rssi_min = -49
        ret = self.filter.is_match((self.dev, self.adv))

        self.assertFalse(ret)
