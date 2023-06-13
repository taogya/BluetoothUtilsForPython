# DjangoBleak
This library save BLE filter and result with "bleak" to models on Django.  
For example use this at Django on Raspberry Pi .

# Installation
## package install
```sh
$ pip install git+https://github.com/taogya/DjangoBleak.git
$ pip freeze
```

## modify django settings
```sh
$ vi settings.py
INSTALLED_APPS = [
    :
    'django_bleak',
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

## Scanner
### BleScanFilter
You create advertising data filter condition.
| column            | constraint    | type       | default | note              | ex.
| -                 | -             | -          | -       | -                 | -
| id                | pk            | BigInteger | auto    | -                 | 1
| note              | 256 char max  | Text       | null    | note              | filter-001, etc...
| is_enabled        | non null      | Boolean    | True    | "True" is enabled | True
| mac_addr          |               | MACAddress | null    | mac address       | 12:34:56:78:90:AB
| rssi_min          | -100 to 0     | Integer    | -100    | minimum rssi      | -100
| rssi_max          | -100 to 0     | Integer    | 0       | maximum rssi      | 0
| company_code      | 0 to 65535    | Integer    | null    | company code      | 0xFFFF
| manufacturer_data | 1024 char max | Text       | null    | regex, hex string | r'^626C65(34|35)2E30$'
| service_uuid      | -             | UUID       | null    | service uuid      | 01234567-0123-0123-0123-0123456789AB
| service_data      | 1024 char max | Text       | null    | regex, hex string | r'^626C65(34|35)2E30$'

### BleScanEvent
You or ble_scanner create scanner event.
| column     | constraint        | type       | default | note                                | ex.
| -          | -                 | -          | -       | -                                   | -
| name       | pk<br>32 char max | Text       | -       | event name                          | ScanEvent001
| is_enabled | non null          | Boolean    | False   | "True" is enabled                   | True
| pid        |                   | Integer    | null    | null is no operating                | 12345
| interval   | non null          | Float      | 3.0     | monitoring interval of "is_enabled" | 3.0

### BleScanDevice
ble_scanner create scanned device.
| column   | constraint    | type       | default | note              | ex.
| -        | -             | -          | -       | -                 | -
| mac_addr | pk            | MACAddress | -       | mac address       | 12:34:56:78:90:AB
| note     | 256 char max  | Text       | null    | note              | device-001, etc...

### BleScanResult
ble_scanner create scanned result.
| column            | constraint        | type       | default | note              | ex.
| -                 | -                 | -          | -       | -                 | -
| id                | pk                | BigInteger | auto    | -                 | 1
| received_at       | non null          | DateTime   | -       | received datetime | 2023-01-01T12:23:45.123456+09:00
| device            | non null, cascade | ForeignKey | -       | to BleScanDevice  | 12:34:56:78:90:AB
| local_name        | 256 char max      | Text       | null    | local name        | device-001, etc...
| rssi              | non null          | Integer    | -       | received rssi     | -100
| company_code      | 0 to 65535        | Integer    | null    | company code      | 0xFFFF
| manufacturer_data | 256 byte max      | Text       | null    | binary data       | b'\x01\x02\x03\0x04'
| service_uuid      | -                 | UUID       | null    | service uuid      | 01234567-0123-0123-0123-0123456789AB
| service_data      | 256 byte max      | Text       | null    | binary data       | b'\x01\x02\x03\0x04'


# Command
## ble_scanner
scan ble advertising data.
```
+--------+ advertising +-------------+
| device |    --->     | ble_scanner | -> is matches BleScanFilter?
|        |     <-scan- |             |    -yes-> create BleScanDevice
+--------+             +-------------+           create BleScanResult
     : 
```
```sh
$ python manage.py ble_scanner ScanEvent001 &
```

if stop ble_scanner, switch "is_enabled" to be False in BleScanEvent.  
"is_enabled" in BleScanEvent is checked at specified "interval" in BleScanEvent.
