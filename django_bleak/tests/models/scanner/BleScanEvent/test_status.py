

import os
from unittest.mock import MagicMock, patch

import psutil
from django.test import TestCase
from django_bleak.models import BleScanEvent


class Test(TestCase):
    """
        No | pid   | is_running | is_enabled | Return
        01 | null  |            |          t | Error
        02 | null  |            |          f | Waitting
        03 | reuse |          f |            | Killed
        04 | me    |          t |          f | Zombie
        05 | me    |          t |          t | Running
    """

    def test_all(self):
        with patch('django_bleak.models.scanner.psutil.Process.is_running') as mock:
            # 01
            self.assertEqual(BleScanEvent(is_enabled=True).status,
                             BleScanEvent.Status.Error)
            # 02
            self.assertEqual(BleScanEvent(is_enabled=False).status,
                             BleScanEvent.Status.Waitting)
            # 03
            mock.return_value = False
            self.assertEqual(BleScanEvent(pid=1, is_enabled=False).status,
                             BleScanEvent.Status.Killed)
            mock.return_value = False
            self.assertEqual(BleScanEvent(pid=1, is_enabled=True).status,
                             BleScanEvent.Status.Killed)
            # 04
            mock.return_value = True
            self.assertEqual(BleScanEvent(pid=1, is_enabled=False).status,
                             BleScanEvent.Status.Zombie)
            # 05
            mock.return_value = True
            self.assertEqual(BleScanEvent(pid=1, is_enabled=True).status,
                             BleScanEvent.Status.Running)
