
from contextlib import ExitStack
from unittest.mock import patch

from django.test import TestCase
from django_bleak.models.scanner import CustomQueryset


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

    def test_self_empty(self):
        self.stack.enter_context(
            patch(
                'django_bleak.models.scanner.CustomQueryset.__iter__',
                return_value=iter([])
            )
        )
        data_list = [(None, None)]
        ret = CustomQueryset().filter_data(data_list)

        self.assertEqual(ret, [])

    def test_data_list_empty(self):
        self.stack.enter_context(
            patch(
                'django_bleak.models.scanner.CustomQueryset.__iter__',
                return_value=iter([MockModel(False), MockModel(True)])
            )
        )
        data_list = []
        ret = CustomQueryset().filter_data(data_list)

        self.assertEqual(ret, [])

    def test_is_match_false(self):
        self.stack.enter_context(
            patch(
                'django_bleak.models.scanner.CustomQueryset.__iter__',
                return_value=iter([MockModel(False)])
            )
        )
        data_list = [(None, None)]
        ret = CustomQueryset().filter_data(data_list)

        self.assertEqual(ret, [])

    def test_is_match_true(self):
        self.stack.enter_context(
            patch(
                'django_bleak.models.scanner.CustomQueryset.__iter__',
                return_value=iter([MockModel(True)])
            )
        )
        data_list = [(None, None)]
        ret = CustomQueryset().filter_data(data_list)

        self.assertEqual(ret, [(None, None)])
