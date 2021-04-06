from kafka import KafkaConsumer 
from kafka import KafkaProducer 
from json import loads 
from json import dumps 
import requests
import threading
import json
import random

from requests import status_codes
BOOTSTRAP_SERVERS = ['sykang-kafka.default.svc.cluster.local:9092']


class DeliveryManager():
    producer = KafkaProducer(acks=0, compression_type='gzip',security_protocol="SSL" ,bootstrap_servers=BOOTSTRAP_SERVERS, value_serializer=lambda v: json.dumps(v, sort_keys=True).encode('utf-8')) 
    ret_fin = 0
    ret_message = ''

    def register_kafka_listener(self, topic):
        # Poll kafka
        def poll():
            # Initialize consumer Instance
            consumer = KafkaConsumer(topic,security_protocol="SSL" , bootstrap_servers=BOOTSTRAP_SERVERS, auto_offset_reset='earliest', enable_auto_commit=True, 
                                        group_id='my-mc' )

            print("About to start polling for topic:", topic)
            consumer.poll(timeout_ms=6000)
            print("Started Polling for topic:", topic)
            for msg in consumer:
                self.kafka_listener(msg)
        print("About to register listener to topic:", topic)
        t1 = threading.Thread(target=poll)
        t1.start()
        print("started a background thread")

    def on_send_success(self, record_metadata):
        print("topic: %s" % record_metadata.topic)
        self.ret_fin = 200
        self.ret_message = "successkafkacheckuser"

    def on_send_error(self, excp):
        print("error : %s" % excp)
        self.producer.flush() 
        self.ret_fin = 400
        self.ret_message = "failkafkacheckuser"

    def sendkafka(self, topic,data, status):
        data['status'] = status
        self.producer.send( topic, value=data).add_callback(self.on_send_success).add_errback(self.on_send_error) 
        self.producer.flush() 


    def kafka_listener(self, data):
        json_data = json.loads(data.value.decode("utf-8"))
        success_credit = random.randrange(0,99)
        if success_credit > 50:
            self.sendkafka("orderkafka", json_data, "success-kafka-delivery")           
        else :
            self.sendkafka("orderkafka", json_data, "fail-kafka-delivery")           

        print( {'message': json_data }, self.ret_fin )


         
if __name__ == '__main__':
#    OrderManager.register_kafka_listener('orderkafka')
#   app.run(host="0.0.0.0", port=5052,debug=True)
    deleverymanager = DeliveryManager()
    deleverymanager.register_kafka_listener('deliverykafka')