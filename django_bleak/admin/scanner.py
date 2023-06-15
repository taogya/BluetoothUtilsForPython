# Register your models here.
import logging

from rangefilter.filters import DateTimeRangeFilterBuilder

from django.contrib import admin, messages
from django.core.management import call_command
from django.utils.translation import gettext_lazy as _
from django_bleak import models

logger = logging.getLogger('general')


@admin.register(models.BleScanFilter)
class BleScanFilterAdmin(admin.ModelAdmin):
    list_display = ('id', 'note', 'is_enabled')
    list_editable = ('note', 'is_enabled',)
    list_per_page = 100
    list_max_show_all = 1000


@admin.register(models.BleScanEvent)
class BleScanEventAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_enabled', 'pid', 'interval')
    list_editable = ('is_enabled',)
    list_per_page = 100
    list_max_show_all = 1000
    actions = ('run_scan_event',)

    def run_scan_event(self, request, queryset):
        if models.BleScanEvent.objects.filter(is_enabled=True).count() > 0:
            messages.error(request,
                           _('already exists running process.' +
                             'you need to stop running process.'))
        elif queryset.count() != 1:
            messages.error(request,
                           _('please select one scan event.'))
        else:
            try:
                call_command('ble_scanner', queryset.first().name)
            except BaseException:
                logger.exception('ble_scanner error')
                messages.error(request,
                               _('execution failed.'))
    run_scan_event.short_description = _('run selected scan event')


@admin.register(models.BleScanDevice)
class BleScanDeviceAdmin(admin.ModelAdmin):
    list_display = ('mac_addr', 'note')
    list_display_links = ('mac_addr', )
    list_editable = ('note',)
    list_per_page = 100
    list_max_show_all = 1000


@admin.register(models.BleScanResult)
class BleScanResultAdmin(admin.ModelAdmin):
    list_display = ('received_at', 'device', 'tx_power', 'rssi', 'company_code', 'service_uuid')
    list_display_links = ('received_at', )
    list_filter = (('received_at', DateTimeRangeFilterBuilder()), 'device', 'company_code', 'service_uuid')
    list_per_page = 100
    list_max_show_all = 1000

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
