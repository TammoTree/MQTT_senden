import network  
from umqtt.simple import MQTTClient
import time
from HTU2X import HTU21D
from bh1750 import BH1750
import json
from machine import Pin, SoftI2C



MQTT_SERVER = "10.50.217.98"
CLIENT_ID = "MQTT_BAUM"
MQTT_TOPIC_UMWELT = "BZTG/Ehnern/Umweltdaten"
MQTT_TOPIC_TASTER = "BZTG/Ehnern/Taster"

i2c = SoftI2C(scl=Pin(22), sda=Pin(21))
htu = HTU21D(22,21)
bh = BH1750(i2c)

wlan = network.WLAN(network.STA_IF)     #Objekt wlan als station interface

wlan.active(True)                       #System einschalten

if not wlan.isconnected():              #Wenn Wlan nicht verbunden ist -> 

    wlan.connect("BZTG-IoT", "WerderBremen24")      #Wlan verbinden

    while not wlan.isconnected():                   #Solange es nicht verbunden ist -> mache nichts

        pass

    print("Netzwerkkonfiguration: ", wlan.ifconfig())   #Netzwerkinfos ausgeben (IP Adresse, Subnetzmaske, Gateway, DNS-Server)

led_gruen = Pin(17, Pin.OUT)
taster = Pin(15, Pin.IN)

was_off_before = True
led_on = False
#-----------------------------------------------------------------------------------------------------------------------------------------

while True:
    temperatur_HTU = int(htu.temperature)
    luftfeuchtigkeit_HTU = int(htu.humidity)
    helligkeit_BH = int(bh.luminance(0x11))

    mqtt_Baum = MQTTClient(CLIENT_ID, MQTT_SERVER)
    mqtt_Baum.connect()

    
    eingang = taster.value()
    if eingang and was_off_before:
        led_on = not led_on
        was_off_before = False
        anzeige_Werte = {
                "Anzeige": led_on
                }
        ausgabe = json.dumps(anzeige_Werte)
        mqtt_Baum.publish(MQTT_TOPIC_TASTER, ausgabe)
        
    if not eingang:
        was_off_before = True
    if led_on:
        led_gruen.on()
    else:
        led_gruen.off()


    data_Werte = {
        "Raum_Ehner_101" :[
            {
                "Temperatur": temperatur_HTU,
                "Luftfeuchtigkeit": luftfeuchtigkeit_HTU,
                "Helligkeit": helligkeit_BH
            }
        ]    
    }

    print("MQTT verbunden!")

    mqtt_Baum.publish(MQTT_TOPIC_UMWELT,json.dumps(data_Werte))
    mqtt_Baum.disconnect()

