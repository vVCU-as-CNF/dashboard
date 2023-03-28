import json
import math
import signal
import socket
import sys
import time

import paho.mqtt.client as mqtt

broker_host = "10.255.28.57"
broker_port = 1883
virtual_itss_id = 3306

def create_clients():
    mqtt_clients = []
    
    client = mqtt.Client("cpm_messages")
    client.on_message = cpm_message_callback
    client.connect(broker_host, broker_port)
    subscribe_topic = "obu/inqueue/json/{}/CPM".format(virtual_itss_id)
    #subscribe_topic = "obu/inqueue/json/3306/CPM"
    client.subscribe(subscribe_topic)
    mqtt_clients.append(client)

    return mqtt_clients

def cpm_message_callback(client, userdata, message):
    json_dict = []
    try:
        json_data = json.loads(str(message.payload.decode("utf-8")))

    except Exception as e:
        print(e)
        return

    print(json_data)
    rsu_latitude = int(json_data['CPM']['cpm']['cpmParameters']['managementContainer']['referencePosition']['latitude']) / 10000000
    rsu_longitude = int(json_data['CPM']['cpm']['cpmParameters']['managementContainer']['referencePosition']['longitude']) / 10000000

    if ('perceivedObjectContainer' not in json_data['CPM']['cpm']['cpmParameters']):
        return

    for perceived_object in json_data['CPM']['cpm']['cpmParameters']['perceivedObjectContainer']:
        object_x = int(perceived_object['PerceivedObject']['xDistance']['value'])
        object_y =  int(perceived_object['PerceivedObject']['yDistance']['value'])
        object_id = int(perceived_object['PerceivedObject']['objectID'])
        
        object_latitude = rsu_latitude + (object_y / 6371000 / 100) * (180 / math.pi)
        object_longitude = rsu_longitude + ((object_x / 6371000 / 100) * (180 / math.pi)) / math.cos(((rsu_latitude + (object_y / 6371000 / 100) * (180 / math.pi)) * math.pi) / 180)

        json_dict.append({'metric': '{}'.format(len(json_dict)), 'latitude': object_latitude, 'longitude': object_longitude})
        
    json_string = json.dumps(json_dict)
    publish_topic = "obu/outqueue/json/{}/perceivedObjects".format(virtual_itss_id)
    client.publish(publish_topic, json_string)


def signal_handler():
    print("Got SIGINT...")

def main():
    print("Creating MQTT client...")
    clients = create_clients()

    for client in clients:
        client.loop_start()
    
    print("Start looping...")
    signal.signal(signal.SIGINT, signal_handler)
    signal.pause()

    for client in clients:
        client.loop_stop()

main()
