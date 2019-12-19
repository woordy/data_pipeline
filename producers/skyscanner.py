import os
import requests
import json
import datetime
import time
import random
import boto3


def browse_quotes(origin, destination, departure_date, return_date='', country='US', currency='USD', locale='en-US'):
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
    base_url = os.environ.get('base_url')

    url = base_url + "{0}/{1}/{2}/{3}-sky/{4}-sky/{5}" \
        .format(country, currency, locale, origin, destination, departure_date)

    querystring = {"inboundpartialdate": return_date}

    headers = {
        'x-rapidapi-host': os.environ.get('x_rapidapi_host'),
        'x-rapidapi-key': os.environ.get('x_rapidapi_key')
    }
    response = requests.request("GET", url, headers=headers, params=querystring)

    return response.text


if __name__ == '__main__':

    # Top 30th biggest airports
    airports = ['ATL', 'LAX', 'ORD', 'DFW', 'DEN', 'JFK', 'SFO', 'SEA', 'LAS', 'MCO',
                'EWR', 'CLT', 'PHX', 'IAH', 'MIA', 'BOS', 'MSP', 'FLL', 'DTW', 'PHL',
                'LGA', 'BWI', 'SLC', 'SAN', 'IAD', 'DCA', 'MDW', 'TPA', 'PDX', 'HNL']

    # departing any day and returning any day
    departure_date_ = 'anytime'
    return_date_ = 'anytime'

    s3_bucket = 'f-project-2019'
    # continue to get pricing
    record_num = 0
    while True:

        # randomly select an origin and departure airport
        origin_ = airports[random.randint(0, len(airports) - 1)]
        destination_ = airports[random.randint(0, len(airports) - 1)]

        # check for a random case where origin == destination
        if origin_ == destination_:
            origin_ = airports[0] if origin_ != airports[0] else airports[1]

        prices_str = browse_quotes(origin=origin_, destination=destination_, departure_date=departure_date_,
                                   return_date=return_date_)
        prices_json = json.loads(prices_str)
        # check to see if values were returned:
        if bool(prices_json):
            f_name = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + '-' + str(record_num) + '.json'
            s3 = boto3.resource('s3')
            s3object = s3.Object(s3_bucket, f_name)

            s3object.put(
                Body=(bytes(json.dumps(prices_json).encode('UTF-8')))
            )
            record_num += 1
            # Wait 80- seconds so as not to exceed rate limit
            print('Generated pricing from: {} to {}'.format(origin_, destination_))
            time.sleep(80)
