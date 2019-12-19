import os

import psycopg2


class PostgresConsumer:
    CONSUMER_GROUP = os.environ['CONSUMER_GROUP']
    POSTGRES_HOST = os.environ['POSTGRES_SERVER_IP']
    POSTGRES_PORT = os.environ['POSTGRES_PORT']
    POSTGRES_DB = os.environ['POSTGRES_DB']
    POSTGRES_USER = os.environ['POSTGRES_USER']
    POSTGRES_PASSWORD = os.environ['POSTGRES_PASSWORD']

    def __init__(self):

        try:
            print('host: ', self.POSTGRES_HOST)
            print('port: ', self.POSTGRES_PORT)

            self.conn = psycopg2.connect(host=self.POSTGRES_HOST, port=self.POSTGRES_PORT,
                                         database=self.POSTGRES_DB, user=self.POSTGRES_USER,
                                         password=self.POSTGRES_PASSWORD)

            print('Successfully connected to postgress')
            self.cursor = self.conn.cursor()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            print('there was an error connecting to postgress*********')

    def insert_country(self, country):
        try:
            self.cursor.execute(
                "INSERT INTO data_app_country (country) VALUES (%s)",
                [country])
            self.conn.commit()
            print('Inserted Country to database: ', country)
        except psycopg2.errors.UniqueViolation as e:
            self.conn.rollback()
            print('Country is already in the database: ', country)

    def insert_place_type(self, placetype):
        try:
            self.cursor.execute(
                "INSERT INTO data_app_placetype (type) VALUES (%s)",
                [placetype])
            self.conn.commit()
            print('Inserted Placetype to database: ', placetype)
        except psycopg2.errors.UniqueViolation as e:
            self.conn.rollback()
            print('Placetype is already in the database: ', placetype)

    def insert_city(self, city_id, city, country_name):
        try:
            self.cursor.execute(
                "INSERT INTO data_app_city (city_id, city, country_name_id) VALUES( %s, %s, (SELECT country from data_app_country WHERE country=%s) )",
                [city_id, city, country_name])
            self.conn.commit()
            print('Inserted City to database: {}, {}'.format(city, country_name))
        except psycopg2.errors.UniqueViolation as e:
            self.conn.rollback()
            print('City is already in the database: ', city)

    def insert_place(self, place_id, iata_code, name, skyscanner_code, city_id, type_id):
        try:
            self.cursor.execute(
                "INSERT INTO data_app_place (place_id, iata_code, name, skyscanner_code, city_id, type_id) VALUES( %s, %s, %s, %s, (SELECT city_id from data_app_city WHERE city_id=%s), (SELECT type from data_app_placetype WHERE type=%s) )",
                [place_id, iata_code, name, skyscanner_code, city_id, type_id])
            self.conn.commit()
            print('Inserted Airport to database: {}'.format(name))
        except psycopg2.errors.UniqueViolation as e:
            self.conn.rollback()
            print('Airport is already in the database: ', name)

    def insert_carrier(self, carrier_id, name):
        try:
            self.cursor.execute(
                "INSERT INTO data_app_carrier (carrier_id, name) VALUES (%s, %s)",
                [carrier_id, name])
            self.conn.commit()
            print('Inserted Airline to database: ', name)
        except psycopg2.errors.UniqueViolation as e:
            self.conn.rollback()
            print('Airline is already in the database: ', name)

    def insert_AVGTicketPriceByDeparture(self, departure_date,  place_id_origin_id,  place_id_dest_id,  count,
                                         total_sum):
        print('entering these values')
        print(departure_date,  place_id_origin_id,  place_id_dest_id,  count, total_sum)
        try:
            self.cursor.execute(
                "INSERT INTO data_app_avgticketpricebydeparture (departure_date,  place_id_origin_id, place_id_dest_id, count, sum) VALUES( %s, (SELECT place_id from data_app_place WHERE place_id=%s), (SELECT place_id from data_app_place WHERE place_id=%s), %s, %s )",
                [departure_date,  place_id_origin_id,  place_id_dest_id,  count, total_sum])
            self.conn.commit()
            print('Inserted Average to database: Departing: {} From: {}:  To: {} Count: {}, sum: {}'.format(departure_date,  place_id_origin_id,  place_id_dest_id, count, total_sum))
        except psycopg2.errors.UniqueViolation as e:
            self.conn.rollback()
            print('Data already in the database: ', e)





