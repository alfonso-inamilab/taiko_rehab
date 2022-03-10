import sys, ftd2xx as ftd

#some MPU6050 Registers and their Address
PWR_MGMT_1   = 0x6B
SMPLRT_DIV   = 0x19
CONFIG       = 0x1A
GYRO_CONFIG  = 0x1B
INT_ENABLE   = 0x38
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F
GYRO_XOUT_H  = 0x43
GYRO_YOUT_H  = 0x45
GYRO_ZOUT_H  = 0x47

d = ftd.open(0)    # Open first FTDI device
print(d.getDeviceInfo())

# def MPU_Init():
# 	#write to sample rate register
# 	bus.write_byte_data(Device_Address, SMPLRT_DIV, 7)
	
# 	#Write to power management register
# 	bus.write_byte_data(Device_Address, PWR_MGMT_1, 1)
	
# 	#Write to Configuration register
# 	bus.write_byte_data(Device_Address, CONFIG, 0)
	
# 	#Write to Gyro configuration register
# 	bus.write_byte_data(Device_Address, GYRO_CONFIG, 24)
	
# 	#Write to interrupt enable register
# 	bus.write_byte_data(Device_Address, INT_ENABLE, 1)

def ft_write(d, data):
    s = str(bytearray(data)) if sys.version_info<(3,) else bytes(data)
    return d.write(s)
 
ft_write(d, [OP]*4 + [0])

def ft_read(d, nbytes):
    s = d.read(nbytes)
    print ("pichi")
    return [ord(c) for c in s] if type(s) is str else list(s)

try:
    while True:
        print(ft_read(d, 1))
except KeyboardInterrupt:
    print("test finished...")