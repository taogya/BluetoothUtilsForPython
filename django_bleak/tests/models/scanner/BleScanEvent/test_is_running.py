

from unittest.mock import patch

from django.test import TestCase
from django_bleak.models import BleScanEvent


class Test(TestCase):

    def test_true(self):
        obj = BleScanEvent()
        with patch('django_bleak.models.scanner.BleScanEvent.status', property(lambda self: BleScanEvent.Status.RUNNING)):
            self.assertTrue(obj.is_running)
        with patch('django_bleak.models.scanner.BleScanEvent.status', property(lambda self: BleScanEvent.Status.ZOMBIE)):
            self.assertTrue(obj.is_running)

    def test_false(self):
        obj = BleScanEvent()
        with patch('django_bleak.models.scanner.BleScanEvent.status', property(lambda self: BleScanEvent.Status.WAITTING)):
            self.assertFalse(obj.is_running)
        with patch('django_bleak.models.scanner.BleScanEvent.status', property(lambda self: BleScanEvent.Status.KILLED)):
            self.assertFalse(obj.is_running)
        with patch('django_bleak.models.scanner.BleScanEvent.status', property(lambda self: BleScanEvent.Status.ERROR)):
            self.assertFalse(obj.is_running)
