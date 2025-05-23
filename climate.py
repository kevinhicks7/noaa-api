import os
import requests
import datetime
import json
from atproto import Client, Request, models

def query_api(cat,params):
    #docs: https://www.ncdc.noaa.gov/cdo-web/webservices/v2
    ncdc_api_key = os.environ.get('NOAA_API') # use reqeusted noaa api token
    if ncdc_api_key is None:
        print('no api key found')
        exit()
    headers = {'token': ncdc_api_key}
    base_url = 'https://www.ncei.noaa.gov/cdo-web/api/v2/'

    filters = "&".join(f"{param}={val}" for param, val in params.items())
    query_url = base_url + cat + '?' + filters
    response = requests.get(query_url, headers=headers)

    if response == {}:
        return {}
    else:
        return dict(response.json())

def get_cities(loc_params):
    cities = []
    offset = 0
    while True:
        loc_params['offset'] = str(offset)
        loc_batch = query_api(cat='locations',params=loc_params)
        if 'results' not in loc_batch.keys() or len(loc_batch['results']) == 0:
            break
        else:
            cities += loc_batch['results']
            offset += 1000
    return cities

def eval_city_data(city,data_params):
    data_params['locationid':city['id']]
    data = query_api('data',data_params)
    #evaluate data
    #post if there's something noteworthy

def post(quote):
    client = Client(request=request)
    pw = os.environ.get('BSKY_CLIMATE_BOT_PW') # from generated app password in bsky
    if pw is None:
        print('no bsky account password found')
        exit()
    client.login('climate-bot.bsky.social', pw)

    text = ''
    client.send_post(text=text)

def main() -> None:
    #today = datetime.now()
    loc_params = {'datasetid':'GHCND',
                  'locationcategoryid':'CITY',
                  'limit':'1000'}
    cities = get_cities(loc_params)
    us_cities = [city for city in cities if city['id'].startswith('CITY:US')]
    print(len(us_cities))
    data_params = {'datasetid':'GHCND',
                   'startdate':'2010-05-01',
                   'enddate':'2010-05-01'}
    #for city in us_cities:
    #    eval_city_data(data_params,city)

if __name__ == '__main__':
    main()
