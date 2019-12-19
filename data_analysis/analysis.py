import psycopg2
import dask.dataframe as dd
import os
import datetime
import pandas as pd
from django import forms

class PriceAnalytics:
    DATABASE_URI = DATABASE_URI = 'postgresql+psycopg2://{user}:{password}@{postgres_server}/{database}'.\
        format(user=os.environ['POSTGRES_USER'],
               password=os.environ['POSTGRES_PASSWORD'],
               postgres_server=os.environ['POSTGRES_SERVER_IP'],
               database=os.environ['POSTGRES_DB'])

    TABLE_AVG_TICKET_BY_DEPARTURE = 'data_app_avgticketpricebydeparture'

    def get_average_tickets_by_source_destination(self, originId, destinationId, start_date, end_date):
        df = dd.read_sql_table(table=self.TABLE_AVG_TICKET_BY_DEPARTURE, uri=self.DATABASE_URI,
                               npartitions=10, index_col='id')
        df['departure_date'] = df['departure_date'].dt.tz_localize(None)
        result = df[(df['place_id_origin_id'] == originId) &
                    (df['place_id_dest_id'] == destinationId) &
                    (df['departure_date'] >= pd.Timestamp(start_date)) &
                    (df['departure_date'] <= pd.Timestamp(end_date))]

        if len(result) == 0:
            return None, None
        total_count = result['count'].sum()
        total_sum = result['sum'].sum()
        average = total_sum / total_count
        result['average'] = result['sum'] / result['count']
        return average.compute(), result.compute()




