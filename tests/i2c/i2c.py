from usb_iss import UsbIss, defs


# Configure I2C mode
iss = UsbIss()
iss.open("COM3")
iss.setup_i2c()

# Write and read back some data
# NOTE: I2C methods use 7-bit device addresses (0x00 - 0x7F)

iss.i2c.write(0x62, 0, [0, 1, 2]);
data = iss.i2c.read(0x62, 0, 3)

print(data)
# [0, 1, 2]