from umqtt.simple import MQTTClient

def do_connect():
    import network
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect('ssid', 'password')
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ifconfig())



do_connect()

c = MQTTClient("varnalab_client","broker.hivemq.com")

c.connect()
c.publish(b"varnalab", b"здрасти")
c.disconnect()