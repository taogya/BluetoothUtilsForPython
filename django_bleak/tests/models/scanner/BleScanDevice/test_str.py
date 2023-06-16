
from django.test import TestCase
from django_bleak.models.scanner import BleScanDevice


class Test(TestCase):

    def test_note_none(self):
        obj = BleScanDevice.objects.create(mac_addr='12:34:56:78:90:AB')

        self.assertEqual(str(obj), '12:34:56:78:90:AB: -')

    def test_note_not_none(self):
        obj = BleScanDevice.objects.create(mac_addr='12:34:56:78:90:AB',
                                           note='note')

        self.assertEqual(str(obj), '12:34:56:78:90:AB: note')
