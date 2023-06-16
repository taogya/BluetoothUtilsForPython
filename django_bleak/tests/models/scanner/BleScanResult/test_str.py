
from django.test import TestCase
from django_bleak.models.scanner import BleScanDevice, BleScanResult


class Test(TestCase):

    def test_default(self):
        dev = BleScanDevice.objects.create(mac_addr='12:34:56:78:90:AB')
        obj = BleScanResult.objects.create(received_at='2023-01-02T12:34:45:678123+09:00',
                                           device=dev,
                                           rssi=-50)

        self.assertEqual(str(obj), '12:34:56:78:90:AB: 2023-01-02T12:34:45:678123+09:00')
