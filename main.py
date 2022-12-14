import machine
import sds011
import bme280 as bme280
import time
import struct
from sx127x import TTN, SX127x
from machine import Pin, SPI
from config import *
import json
import math
import network

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


def do_connect():
    import network
    sta_if = network.WLAN(network.STA_IF)
    sta_if.config(hostname="Micropython-Weather")
    
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect(wifi_config['ssid'], wifi_config['password'])
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ifconfig())


lora.on_receive(on_receive)
lora.receive()


do_connect()

while True:
    
    dust_sensor.wake()
    time.sleep(5)
    
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
    
    dust_sensor.sleep()
     
    temperature,pressure,humidity = bme.values

    temp = math.ceil(float(temperature[:-1]))
    press = math.ceil(float(pressure[:-3]))
    hum = math.ceil(float(humidity[:-1]))
    
    
    print(f"{temp},{press},{hum},{pm10},{pm25}")

    payload = struct.pack('>IIIdd',temp,press,hum,pm25,pm10) #struct format int,int,int,double,double
    lora.send_data(data=payload, data_length=len(payload), frame_counter=frame_counter)
    lora.receive()
    
    frame_counter += 1

    for i in range(app_config['loop']):
        time.sleep_ms(app_config['sleep'])