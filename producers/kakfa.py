from kafka import KafkaProducer, SimpleClient
from kafka.admin import KafkaAdminClient, NewTopic
import requests
import json
import time
import random
import uuid
import datetime
import os
import boto3

class SkyScanner:

    AIRPORTS = ['ATL', 'LAX', 'ORD', 'DFW', 'DEN', 'JFK', 'SFO', 'SEA', 'LAS', 'MCO',
                    'EWR', 'CLT', 'PHX', 'IAH', 'MIA', 'BOS', 'MSP', 'FLL', 'DTW', 'PHL',
                    'LGA', 'BWI', 'SLC', 'SAN', 'IAD', 'DCA', 'MDW', 'TPA', 'PDX', 'HNL']

    # departing any day and returning any day
    DEPARTURE_DATE = 'anytime'
    RETURN_DATE = 'anytime'

    def __init__(self):
        self.base_url = os.environ.get('base_url')
        self.host = os.environ.get('x_rapidapi_host')
        self.key = os.environ.get('x_rapidapi_key')

    def get_ticket_quotes(self, origin, destination, departure_date,
                          return_date='', country='US', currency='USD', locale='en-US'):
        """
        :param origin: 2 digit code of originating airport .e.g ABE
        :param destination:  2 digit code of destination airport .e.g JFK
        :param departure_date: The departing date. Format “yyyy-mm-dd”, “yyyy-mm” or “anytime”.
        :param return_date: The return date. Format “yyyy-mm-dd”, “yyyy-mm” or “anytime”. Use empty string for oneway trip.
        :param country: The market country user is in e.g US
        :param currency: The currency you want the prices in
        :param locale: The locale you want the results in (ISO locale) e.g en-US
        :return:
        """

        url = self.base_url + "{0}/{1}/{2}/{3}-sky/{4}-sky/{5}" \
            .format(country, currency, locale, origin, destination, departure_date)

        querystring = {"inboundpartialdate": return_date}

        headers = {
            'x-rapidapi-host': self.host,
            'x-rapidapi-key': self.key
        }
        response = requests.request("GET", url, headers=headers, params=querystring)

        return response.text

    def generate_quote_parameters(self):

        # randomly select an origin and departure airport
        origin = self.AIRPORTS[random.randint(0, len(self.AIRPORTS) - 1)]
        destination = self.AIRPORTS[random.randint(0, len(self.AIRPORTS) - 1)]

        # check for a random case where origin == destination
        if origin == destination:
            origin = self.AIRPORTS[0] if origin != self.AIRPORTS[0] else self.AIRPORTS[1]

        return origin, destination, self.DEPARTURE_DATE, self.RETURN_DATE


class KafkaStreaming:

    BOOTSTRAP_SERVER = 'kafka:9092'
    REPLICATION_FACTOR = 2
    NUM_PARTITIONS = 6
    TOPIC_NAME = 'ticket-prices'
    S3_BUCKET = 'f-project-2019'

    def create_topic(self):
        client = SimpleClient(self.BOOTSTRAP_SERVER)
        broker_topics = client.topic_partitions
        admin_client = KafkaAdminClient(bootstrap_servers=self.BOOTSTRAP_SERVER, client_id='test')
        if self.TOPIC_NAME and self.TOPIC_NAME not in broker_topics:
            topic_list = [NewTopic(name=self.TOPIC_NAME, num_partitions=self.NUM_PARTITIONS,
                                   replication_factor=self.REPLICATION_FACTOR)]
            try:
                admin_client.create_topics(new_topics=topic_list, validate_only=False)
            except Exception:
                raise Exception('Unable to create topic')
        elif self.TOPIC_NAME and self.TOPIC_NAME in broker_topics:
            print('Topic already created')

    def send_topic(self):
        producer = KafkaProducer(bootstrap_servers=self.BOOTSTRAP_SERVER,
                                 value_serializer=lambda x: json.dumps(x).encode('utf-8'))
        sky_scanner = SkyScanner()

        # Get quotes
        record_num = 0
        while True:
            origin, destination, departure_date, return_date = sky_scanner.generate_quote_parameters()
            quotes = sky_scanner.get_ticket_quotes(origin=origin, destination=destination, departure_date=departure_date,
                                                   return_date=return_date)
            quotes_json = json.loads(quotes)
            # check to see if returned value contains quotes:
            if bool(quotes_json):
                # uu_id = str(uuid.uuid4())
                key = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + '-' + str(record_num)
                s3 = boto3.resource('s3')
                s3object = s3.Object(self.S3_BUCKET, key)

                s3object.put(
                    Body=(bytes(json.dumps(quotes_json).encode('UTF-8')))
                )
                print('File saved to S3: ', key)
                producer.send(topic=self.TOPIC_NAME, value=quotes_json, key=str.encode(str(key)))
                print('Generated pricing from: {} to {}'.format(origin, destination))
                record_num += 1

            # Wait 80- seconds so as not to exceed rate limit
            time.sleep(80)

    def produce(self):
        self.create_topic()
        self.send_topic()


