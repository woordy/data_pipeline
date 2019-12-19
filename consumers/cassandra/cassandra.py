import os

# cassandra
from cassandra.cluster import Cluster


class CassandraConsumer:
    CASSANDRA_NODE_IP = os.environ['CASSANDRA_CLUSTER_SEED_IP']
    KEYSPACE = os.environ['KEYSPACE']
    TABLE = 'Quotes'
    cluster = Cluster([CASSANDRA_NODE_IP], port=int(os.environ['CASSANDRA_PORT']))

    def __init__(self):
        self.session = self.cluster.connect()
        print('successfully connected to cassandra')
        try:
            self.session.execute("""
                    CREATE KEYSPACE IF NOT EXISTS %s
                    WITH replication = { 'class': 'NetworkTopologyStrategy', 'datacenter1' : 1,  'datacenter2' : 2}
                    """ % self.KEYSPACE)
        except Exception:
            print('Unable to create keyspace: {}'.format(self.KEYSPACE))
            # log.info('Unable to create keyspace: {}'.format(self.KEYSPACE))

        # log.info('Setting Keyspace')
        self.session.set_keyspace(self.KEYSPACE)

        self.session.execute("""
                CREATE TABLE IF NOT EXISTS Quotes (
                    quoteId int,
                    minPrice float,
                    direct Boolean,
                    carrierIds int,
                    originId int,
                    destinationId int,
                    departureDate timestamp,
                    quoteDateTime timestamp,
                    PRIMARY KEY ((originId, destinationId), departureDate)
                )
                """)
        # log.info('Table Quotes exists or has been created')

    def insert_quotes(self, quoteId, minPrice, direct, carrierIds, originId, destinationId, departureDate,
                         quoteDateTime):
        self.session.execute(
            "INSERT INTO Quotes (quoteId, minPrice, direct, carrierIds, originId, destinationId, departureDate, quoteDateTime) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            [quoteId, minPrice, direct, carrierIds, originId, destinationId, departureDate, quoteDateTime])
        print("inserted event: ", quoteId, minPrice, direct, carrierIds, originId, destinationId, departureDate,
              quoteDateTime)








