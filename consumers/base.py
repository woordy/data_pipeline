from kafka import KafkaConsumer
import json
from consumers.cassandra import CassandraConsumer
from consumers.postgres import PostgresConsumer


class BaseConsumer:
    CONSUMER_GROUP = 'cassandra-consumer-grp'
    BOOTSTRAP_SERVER = 'kafka:9092'
    TOPICS = ['ticket-prices']
    consumer = KafkaConsumer(bootstrap_servers=BOOTSTRAP_SERVER, group_id=CONSUMER_GROUP,
                             auto_offset_reset='latest')
    consumer.subscribe(TOPICS)
    cassandraConsumer = CassandraConsumer()
    postgresConsumer = PostgresConsumer()

    def format_quotes(self, quote):
        quoteId = quote['QuoteId']
        minPrice = quote['MinPrice']
        direct = quote['Direct']
        carrierIds = quote['OutboundLeg']['CarrierIds'][0]
        originId = quote['OutboundLeg']['OriginId']
        destinationId = quote['OutboundLeg']['DestinationId']
        departureDate = quote['OutboundLeg']['DepartureDate']
        quoteDateTime = quote['QuoteDateTime']
        yield quoteId, minPrice, direct, carrierIds, originId, destinationId, departureDate, quoteDateTime

    def format_places(self, place):
        placeId = place['PlaceId']
        iataCode = place['IataCode']
        name = place['Name']
        ty_pe = place['Type']
        skyscannerCode = place['SkyscannerCode']
        cityName = place['CityName']
        cityId = place['CityId']
        countryName = place['CountryName']

        yield placeId, iataCode, name, ty_pe, skyscannerCode, cityName, cityId, countryName

    def format_carriers(self, carrier):
        carrierId = carrier['CarrierId']
        name = carrier['Name']
        yield carrierId, name

    def parse_lines(self):
        """
        lazy loading and parsing of data with generators
        """
        while True:
            for record in self.consumer:
                record_json = json.loads(record.value)
                if 'Quotes' in record_json:
                    yield record_json

    def consume(self):
        for record in self.parse_lines():
            if record['Places']:
                print('------------------------Places-------------------')
                for place in record['Places']:
                    gen_place = self.format_places(place=place)
                    for placeId, iataCode, name, placetype, skyscannerCode, cityName, cityId, countryName in gen_place:
                        self.postgresConsumer.insert_country(countryName)
                        self.postgresConsumer.insert_city(city_id=cityId, city=cityName, country_name=countryName)
                        self.postgresConsumer.insert_place_type(placetype=placetype)
                        self.postgresConsumer.insert_place(place_id=placeId, iata_code=iataCode,
                                                           name=name, skyscanner_code=skyscannerCode,
                                                           city_id=cityId, type_id=placetype)
            if record['Carriers']:
                print('--------------Carriers------------------------')
                for carrier in record['Carriers']:
                    gen_carrier = self.format_carriers(carrier=carrier)
                    for carrierId, name in gen_carrier:
                        self.postgresConsumer.insert_carrier(carrier_id=carrierId, name=name)

            if record['Quotes']:
                print('--------------------Quotes-------------------')
                print('number of quotes', len(record['Quotes']))
                total = {}
                destinations = {}
                for quote in record['Quotes']:
                    gen_quote = self.format_quotes(quote=quote)
                    for quoteId, minPrice, direct, \
                            carrierIds, originId, destinationId, departureDate, quoteDateTime in gen_quote:
                        self.cassandraConsumer.insert_quotes(quoteId, minPrice, direct, carrierIds, originId,
                                                             destinationId, departureDate, quoteDateTime)
                        if departureDate not in total:
                            total[departureDate] = []
                        total[departureDate].append(minPrice)
                        destinations['originId'] = originId
                        destinations['destinationId'] = destinationId

                print('Average Prices------------ ')
                for departure_date, price in total.items():
                    self.postgresConsumer.\
                        insert_AVGTicketPriceByDeparture(departure_date=departure_date,
                                                         place_id_origin_id=destinations['originId'],
                                                         place_id_dest_id=destinations['destinationId'],
                                                         count=len(price), total_sum=sum(price))
