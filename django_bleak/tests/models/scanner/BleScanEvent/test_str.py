
from django.test import TestCase
from django_bleak.models.scanner import BleScanEvent


class Test(TestCase):

    def test_pid_none(self):
        obj = BleScanEvent.objects.create(name='ScanEvent001')

        self.assertEqual(str(obj), 'ScanEvent001: False/-/3.000sec')

    def test_pid_not_none(self):
        obj = BleScanEvent.objects.create(name='ScanEvent001', pid=1234, create_time=1234.5)

        self.assertEqual(str(obj), 'ScanEvent001: False/1234@1234.5/3.000sec')
