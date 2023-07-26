# DjangoBleak
This library save BLE filter and result with "bleak" to models on Django.  
For example use this at Django on Raspberry Pi .

# Installation
## package install
```sh
$ pip install git+https://github.com/taogya/DjangoBleak.git
```

## modify django settings
```sh
$ vi settings.py
INSTALLED_APPS = [
    :
    'django_bleak',
    'rangefilter',
    :
]
```

## migrations
```sh
$ python manage.py makemigrations
$ python manage.py migrate
```

# Models
This library has models below.

## ER Diagram
![django-bleak-er](/resources/django-bleak-er.png)

### BleScanFilter
You create advertising data filtering condition.
| column            | constraint    | type       | default | note              | ex.
| -                 | -             | -          | -       | -                 | -
| id                | pk            | BigInteger | auto    | -                 | 1
| note              | 256 char max  | Text       | null    | note              | for my-device
| is_enabled        | non null      | Boolean    | True    | "True" is enabled | True
| mac_addr          |               | MACAddress | null    | mac address       | 12:34:56:78:90:AB
| local_name        | 256 char max  | Text       | null    | local name        | device-001
| company_code      | 0 to 65535    | Integer    | null    | company code      | 0xFFFF
| manufacturer_data | 1024 char max | Text       | null    | regex, hex string | r'^626C65(34|35)2E30$'
| service_uuid      | -             | UUID       | null    | service uuid      | 01234567-0123-0123-0123-0123456789AB
| service_data      | 1024 char max | Text       | null    | regex, hex string | r'^626C65(34|35)2E30$'
| rssi_min          | -100 to 0     | Integer    | -100    | minimum rssi      | -100
| rssi_max          | -100 to 0     | Integer    | 0       | maximum rssi      | 0

### BleScanEvent
You or ble_scanner create scanner event.
| column      | constraint        | type    | default | note                                     | ex.
| -           | -                 | -       | -       | -                                        | -
| name        | pk<br>32 char max | Text    | -       | event name                               | ScanEvent001
| is_enabled  | non null          | Boolean | False   | "True" is enabled                        | True
| pid         |                   | Integer | null    | null is no operating                     | 12345
| create_time |                   | Float   | null    | create time, null means no process.      | 1293678383.0799999
| interval    | non null, >= 1.0  | Float   | 3.0     | monitoring interval[sec] of "is_enabled" | 3.0
| scan_mode   | 3 char max        | Text    | itv     | seq: Sequencial scan<br>itv: Interval    | itv

This models has properties, "status", "is_running".
#### status
| pid   | is_running<sup>*</sup> | is_enabled | Return
| -     | -           | -          | -
| null  |         any |       True | Error
| null  |         any |      False | Waitting
| reuse |       False |        any | Killed
| me    |        True |      False | Zombie
| me    |        True |       True | Running

\* is_running is process status.

#### is_running
"True" if status in RUNNING, ZOMBIE


### BleScanDevice
ble_scanner create scanned device.
| column   | constraint   | type       | default | note        | ex.
| -        | -            | -          | -       | -           | -
| mac_addr | pk           | MACAddress | -       | mac address | 12:34:56:78:90:AB
| note     | 256 char max | Text       | null    | note        | device-001

### BleScanResult
ble_scanner create scanned result.
| column            | constraint        | type       | default | note              | ex.
| -                 | -                 | -          | -       | -                 | -
| id                | pk                | BigInteger | auto    | -                 | 1
| received_at       | non null          | DateTime   | -       | received datetime | 2023-01-01T12:23:45.123456+09:00
| device            | non null, cascade | ForeignKey | -       | to BleScanDevice  | 12:34:56:78:90:AB
| local_name        | 256 char max      | Text       | null    | local name        | device-001
| company_code      | 0 to 65535        | Integer    | null    | company code      | 0xFFFF
| manufacturer_data | 256 byte max      | Text       | null    | binary data       | b'\x01\x02\x03\0x04'
| service_uuid      | -                 | UUID       | null    | service uuid      | 01234567-0123-0123-0123-0123456789AB
| service_data      | 256 byte max      | Text       | null    | binary data       | b'\x01\x02\x03\0x04'
| tx_power          | -                 | Float      | null    | tx power[dBm]     | 0
| rssi              | non null          | Float      | -       | rssi[dBm]         | -100


# Command
## ble_scanner
sequencial scan and save ble advertising data.  
If received advertising data, the process validate it immediately.
Received any data during validating is discarded.  
BleScanEvent.is_enabled is checked every BleScanEvent.interval seconds.  
![django-bleak-er](/resources/django-bleak-sequencial.png)
```sh
$ python manage.py ble_scanner ScanEvent001
```
## ble_scanner_interval
interval scan and save ble advertising data.  
Scanning every BleScanEvent.interval seconds, and the process validate them.  
Received any data during validating is discarded.  
BleScanEvent.is_enabled is checked every BleScanEvent.interval seconds.  
![django-bleak-er](/resources/django-bleak-interval.png)
```sh
$ python manage.py ble_scanner_interval ScanEvent001
```

# Appendix
set logger as 'ble_scanner' when use logger.