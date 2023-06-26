

from unittest.mock import patch

from django.test import TestCase
from django_bleak.models import BleScanEvent


class Test(TestCase):

    def test_true(self):
        obj = BleScanEvent()
        with patch('django_bleak.models.scanner.BleScanEvent.status', property(lambda self: BleScanEvent.Status.Running)):
            self.assertTrue(obj.is_running)
        with patch('django_bleak.models.scanner.BleScanEvent.status', property(lambda self: BleScanEvent.Status.Zombie)):
            self.assertTrue(obj.is_running)

    def test_false(self):
        obj = BleScanEvent()
        with patch('django_bleak.models.scanner.BleScanEvent.status', property(lambda self: BleScanEvent.Status.Waitting)):
            self.assertFalse(obj.is_running)
        with patch('django_bleak.models.scanner.BleScanEvent.status', property(lambda self: BleScanEvent.Status.Killed)):
            self.assertFalse(obj.is_running)
        with patch('django_bleak.models.scanner.BleScanEvent.status', property(lambda self: BleScanEvent.Status.Error)):
            self.assertFalse(obj.is_running)
