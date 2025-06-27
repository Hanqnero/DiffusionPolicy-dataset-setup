import hid

for device in hid.enumerate():
    print(f"Vendor ID : {hex(device['vendor_id'])}")
    print(f"Product ID : {hex(device['product_id'])}")
    print(f"Manufacturer : {device['manufacturer_string']}")
    print(f"Product : {device['product_string']}")
    print(f"Serial Number : {device['serial_number']}")
    print(f"Path : {device['path']}")
    print(f"Interface Number: {device['interface_number']}")
    print('-' * 40)