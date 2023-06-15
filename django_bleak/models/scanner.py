
import re
import typing as typ

import bleak as blk
from macaddress.fields import MACAddressField
from regex_field.fields import RegexField

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models, transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

BleScanData = typ.Tuple[blk.BLEDevice, blk.AdvertisementData]


class CustomQueryset(models.QuerySet):

    def filter_data(self, data_list: typ.List[BleScanData]) -> typ.List[BleScanData]:
        """get BleScanData list that matches BleScanFilters

        Args:
            data_list (typ.List[BleScanData]):
                BleScanData list

        Returns:
            typ.List[BleScanData]:
                get BleScanData list that matches BleScanFilters
                return [] if filter is [].
        """
        res = [data
               for f in self
               for data in data_list
               if f.is_match(data)]

        return res

    @transaction.atomic
    def create_data(self, data_list: typ.List[BleScanData]):
        """save result that matches BleScanFilters

        Args:
            data_list (typ.List[BleScanData]): BleScanData list
        """
        received_at = timezone.now()
        filter_data = self.filter_data(data_list)
        addrs = set([dev.address for dev, _ in filter_data])
        devs = {addr: BleScanDevice.objects.get_or_create(mac_addr=addr)[0]
                for addr in addrs}

        scan_results = []
        for (dev, adv) in filter_data:
            scan_results += [
                # for manufacturer_data
                BleScanResult(
                    received_at=received_at,
                    device=devs[dev.address],
                    local_name=adv.local_name,
                    company_code=company_code,
                    manufacturer_data=adv.manufacturer_data[company_code],
                    tx_power=adv.tx_power,
                    rssi=adv.rssi,
                ) for company_code in adv.manufacturer_data
            ] + [
                # for service_data
                BleScanResult(
                    received_at=received_at,
                    device=devs[dev.address],
                    local_name=adv.local_name,
                    service_uuid=service_uuid,
                    service_data=adv.service_data[service_uuid],
                    tx_power=adv.tx_power,
                    rssi=adv.rssi,
                ) for service_uuid in adv.service_data
            ]
        BleScanResult.objects.bulk_create(
            scan_results,
            batch_size=5000,
        )


class CustomManager(models.Manager.from_queryset(CustomQueryset)):
    pass


class BleScanFilter(models.Model):

    id = models.BigAutoField(
        primary_key=True)

    note = models.CharField(
        verbose_name=_('note'),
        help_text=_('for my device'),
        null=True,
        blank=True,
        default=None,
        max_length=256)

    is_enabled = models.BooleanField(
        verbose_name=_('is filter enabled'),
        default=True)

    mac_addr = MACAddressField(
        verbose_name=_('mac address'),
        help_text='12:34:56:78:90:AB',
        null=True,
        blank=True,
        default=None)

    local_name = models.CharField(
        verbose_name=_('local name'),
        help_text=r'device-001',
        null=True,
        blank=True,
        default=None,
        max_length=256)

    company_code = models.IntegerField(
        verbose_name=_('company code'),
        help_text=r'0xFFFF',
        null=True,
        blank=True,
        default=None,
        validators=[MinValueValidator(0),
                    MaxValueValidator(65535)])

    manufacturer_data = RegexField(
        verbose_name=_('regex of manufacturer_data'),
        help_text=r'^626C65(34|35)2E30$',
        null=True,
        blank=True,
        default=None,
        max_length=1024,
        re_flags=re.IGNORECASE)

    service_uuid = models.UUIDField(
        verbose_name=_('service uuid'),
        help_text=r'01234567-0123-0123-0123-0123456789AB',
        null=True,
        blank=True,
        default=None)

    service_data = RegexField(
        verbose_name=_('regex of service_data'),
        help_text=r'^626C65(34|35)2E30$',
        null=True,
        blank=True,
        default=None,
        max_length=1024,
        re_flags=re.IGNORECASE)

    rssi_min = models.IntegerField(
        verbose_name=_('rssi min[dBm]'),
        help_text='default -100[dBm]',
        default=-100,
        validators=[MinValueValidator(-100),
                    MaxValueValidator(0)])

    rssi_max = models.IntegerField(
        verbose_name=_('rssi max[dBm]'),
        help_text='default 0[dBm]',
        default=0,
        validators=[MinValueValidator(-100),
                    MaxValueValidator(0)])

    objects = CustomManager()

    def __str__(self):
        return f'{self.id}: {self.note or "-"}'

    def is_match(self, data: BleScanData) -> bool:
        """is BleScanData matche to filters

        Args:
            data (BleScanData): BleScanData

        Returns:
            bool: True is matching
        """
        dev, adv = data
        if self.mac_addr and str(self.mac_addr) != dev.address:
            return False
        if self.local_name and self.local_name != adv.local_name:
            return False
        if (self.company_code is not None) and (self.company_code not in adv.manufacturer_data.keys()):
            return False
        if self.manufacturer_data and all([self.manufacturer_data.match(v.hex()) is None
                                           for v in adv.manufacturer_data.values()]):
            return False
        if self.service_uuid and self.service_uuid not in adv.service_data.keys():
            return False
        if self.service_data and all([self.service_data.match(v.hex()) is None
                                      for v in adv.service_data.values()]):
            return False
        if not (self.rssi_min <= adv.rssi <= self.rssi_max):
            return False

        return True

    class Meta:
        verbose_name = _('ble scan filter')
        verbose_name_plural = _('ble scan filters')
        db_table = 'django_bleak_blescanfilter'


class BleScanEvent(models.Model):

    DEFAULT_INTERVAL = 3.0

    name = models.CharField(
        primary_key=True,
        verbose_name=_('event name'),
        help_text='ScanEvent001',
        max_length=32)

    is_enabled = models.BooleanField(
        verbose_name=_('is scan enabled'),
        default=False)

    pid = models.IntegerField(
        verbose_name=_('pid'),
        help_text=_('null means no process exists.'),
        null=True,
        blank=True,
        default=None)

    interval = models.FloatField(
        verbose_name=_('monitoring interval of is_enabled [sec]'),
        help_text=_('default 3.0[sec], 0.0 means no monitoring.'),
        default=DEFAULT_INTERVAL,
        validators=[MinValueValidator(0.0)])

    def __str__(self):
        return f'{self.name}: {self.is_enabled}/{self.pid}/{self.interval:.3f}sec'

    class Meta:
        verbose_name = _('ble scan event')
        verbose_name_plural = _('ble scan events')
        db_table = 'django_bleak_blescanevent'


class BleScanDevice(models.Model):

    mac_addr = MACAddressField(
        primary_key=True,
        verbose_name=_('mac address'),
        help_text='12:34:56:78:90:AB')

    note = models.CharField(
        verbose_name=_('note'),
        help_text='device-001',
        null=True,
        blank=True,
        default=None,
        max_length=256)

    def __str__(self):
        return f'{self.mac_addr}: {self.note or "-"}'

    class Meta:
        verbose_name = _('ble scan device')
        verbose_name_plural = _('ble scan devices')
        db_table = 'django_bleak_blescandevice'


class BleScanResult(models.Model):

    id = models.BigAutoField(
        primary_key=True)

    received_at = models.DateTimeField(
        verbose_name=_('received datetime'))

    device = models.ForeignKey(
        verbose_name=_('relational device'),
        to=BleScanDevice,
        on_delete=models.CASCADE)

    local_name = models.CharField(
        verbose_name=_('local name'),
        null=True,
        blank=True,
        default=None,
        max_length=256)

    company_code = models.IntegerField(
        verbose_name=_('company code'),
        null=True,
        blank=True,
        default=None,
        validators=[MinValueValidator(0),
                    MaxValueValidator(65535)])

    manufacturer_data = models.BinaryField(
        verbose_name=_('manufacturer_data'),
        null=True,
        blank=True,
        default=None,
        max_length=256)

    service_uuid = models.UUIDField(
        verbose_name=_('service uuid'),
        null=True,
        blank=True,
        default=None)

    service_data = models.BinaryField(
        verbose_name=_('service_data'),
        null=True,
        blank=True,
        default=None,
        max_length=256)

    tx_power = models.FloatField(
        verbose_name=_('tx_power[dBm]'),
        null=True,
        blank=True,
        default=None)

    rssi = models.FloatField(
        verbose_name=_('rssi[dBm]'))

    class Meta:
        verbose_name = _('ble scan result')
        verbose_name_plural = _('ble scan results')
        db_table = 'django_bleak_blescanresult'
        indexes = [
            models.Index(fields=['device', 'company_code'],
                         name='bsr_dev_com_idx'),
            models.Index(fields=['device', 'service_uuid'],
                         name='bsr_dev_ser_idx'),
            models.Index(fields=['device', 'received_at'],
                         name='bsr_dev_rec_idx'),
            models.Index(fields=['device', 'received_at', 'company_code'],
                         name='bsr_dev_rec_com_idx'),
            models.Index(fields=['device', 'received_at', 'service_uuid'],
                         name='bsr_dev_rec_ser_idx'),
        ]
