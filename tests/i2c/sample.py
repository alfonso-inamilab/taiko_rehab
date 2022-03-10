from pyftdi.i2c import I2cController

ctrl = I2cController()
ctrl.configure('ftdi://ftdi:230x/1')
i2c = ctrl.get_port(0x21)

# send 2 bytes
i2c.write([0x12, 0x34])

# send 2 bytes, then receive 2 bytes
out = i2c.exchange([0x12, 0x34], 2)