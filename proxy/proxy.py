import json
import math
import signal

import paho.mqtt.client as mqtt

broker_host = "10.255.32.4"
broker_port = 1883
virtual_itss_id = 3306

def create_clients():
    mqtt_clients = []

    client = mqtt.Client("cpm_messages")
    client.on_message = cpm_message_callback
    client.connect(broker_host, broker_port)
    subscribe_topic = "obu/inqueue/json/{}/CPM".format(virtual_itss_id)
    client.subscribe(subscribe_topic)
    print("Subscibed to "+subscribe_topic)
    mqtt_clients.append(client)

    return mqtt_clients

def cpm_message_callback(client, userdata, message):
    json_position_dict = []
    json_speed_dict = []
    x_speed_value = 0;
    y_speed_value = 0;
    object_counter = 0
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

    perceived_objects = json_data['CPM']['cpm']['cpmParameters']['perceivedObjectContainer']
    for perceived_object in perceived_objects:
        object_counter += 1
        position_x = int(perceived_object['PerceivedObject']['xDistance']['value'])
        position_y =  int(perceived_object['PerceivedObject']['yDistance']['value'])

        x_speed_value += int(perceived_object['PerceivedObject']['xSpeed']['value'])
        y_speed_value += int(perceived_object['PerceivedObject']['ySpeed']['value'])
        # object_id = int(perceived_object['PerceivedObject']['objectID'])
        
        object_latitude = rsu_latitude + (position_y / 6371000 / 100) * (180 / math.pi)
        object_longitude = rsu_longitude + ((position_x / 6371000 / 100) * (180 / math.pi)) / math.cos(((rsu_latitude + (position_y / 6371000 / 100) * (180 / math.pi)) * math.pi) / 180)

        json_position_dict.append({ 'metric': '{}'.format(len(json_position_dict)), 
                                    'latitude': object_latitude,
                                    'longitude': object_longitude
        })

    ## 

    json_string = json.dumps(json_position_dict)
    publish_topic = "obu/outqueue/json/{}/perceivedObjects/distance".format(virtual_itss_id)

    client.publish(publish_topic, json_string)

    ##

    
    x_speed_value = x_speed_value * 0.036 / object_counter
    y_speed_value = y_speed_value * 0.036 / object_counter

    instant_speed_value = math.sqrt(x_speed_value**2+y_speed_value**2)
    json_speed_dict.append({'xSpeed': x_speed_value,
                            'ySpeed': y_speed_value,
                            'instantSpeed': instant_speed_value
    })

    json_string = json.dumps(json_speed_dict)
    publish_topic = "obu/outqueue/json/{}/perceivedObjects/speed".format(virtual_itss_id)

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
