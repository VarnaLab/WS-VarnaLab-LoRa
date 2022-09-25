#Production!
import machine
import sds011
import bme280 as bme280
import time
import struct
import urandom
from sx127x import TTN, SX127x
from machine import Pin, SPI
from config import *
import json
#from cayennelpp import LppFrame, LppUtil
import math

i2c = machine.I2C(0, sda=machine.Pin(21), scl=machine.Pin(22))
bme = bme280.BME280(i2c=i2c)
uart = machine.UART(2,baudrate=9600, bits=8, parity=None, stop=1, rx=16, tx=17)
dust_sensor = sds011.SDS011(uart)

__DEBUG__ = True

ttn_config = TTN(ttn_config['devaddr'], ttn_config['nwkey'], ttn_config['app'], country=ttn_config['country'])

device_spi = SPI(device_config['spi_unit'], baudrate = 10000000, 
        polarity = 0, phase = 0, bits = 8, firstbit = SPI.MSB,
        sck = Pin(device_config['sck'], Pin.OUT, Pin.PULL_DOWN),
        mosi = Pin(device_config['mosi'], Pin.OUT, Pin.PULL_UP),
        miso = Pin(device_config['miso'], Pin.IN, Pin.PULL_UP))

lora = SX127x(device_spi, pins=device_config, lora_parameters=lora_parameters, ttn_config=ttn_config)

frame_counter = 0

def on_receive(lora, outgoing):
    payload = lora.read_payload()
    print(payload)

lora.on_receive(on_receive)
lora.receive()



while True:
    
    #frame = LppFrame()
    
    dust_sensor.wake()

    #Returns NOK if no measurement found in reasonable time
  
    status = dust_sensor.read()
    #Returns NOK if checksum failed
    pkt_status = dust_sensor.packet_status

    if(status == False):
        print('Measurement failed.')
        pm25,pm10=(0.0,0.0)
    elif(pkt_status == False):
        print('Received corrupted data.')
        pm25,pm10=(0.0,0.0)
    else:
        pm25=float(dust_sensor.pm25)
        pm10=float(dust_sensor.pm10)
        #print('PM25: ', dust_sensor.pm25)
        #print('PM10: ', dust_sensor.pm10)
#     
    temperature,pressure,humidity = bme.values
#     
    #print(f"{temperature},{pressure},{humidity},{pm10},{pm25}")
#     time.sleep(1)
    
    
    temp = math.ceil(float(temperature[:-1]))
    press = math.ceil(float(pressure[:-3]))
    hum = math.ceil(float(humidity[:-1]))
    
    
    print(f"{temp},{press},{hum},{pm10},{pm25}")

    payload = struct.pack('>IIIdd',temp,press,hum,pm25,pm10)
    lora.send_data(data=payload, data_length=len(payload), frame_counter=frame_counter)
    lora.receive()
    
    frame_counter += 1

    for i in range(app_config['loop']):
        time.sleep_ms(app_config['sleep'])