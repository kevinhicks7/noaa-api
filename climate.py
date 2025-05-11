import os
import requests
import datetime
import json
from atproto import Client, Request, models

def query_api(cat,params):
    #docs: https://www.ncdc.noaa.gov/cdo-web/webservices/v2
    ncdc_api_key = os.environ.get('NOAA_API')
    if ncdc_api_key is None:
        print('no api key found')
        exit()
    headers = {'token': ncdc_api_key}
    base_url = 'https://www.ncei.noaa.gov/cdo-web/api/v2/'

    filters = "&".join(f"{param}={val}" for param, val in params.items())
    query_url = base_url + cat + '?'+ filters
    response = requests.get(query_url, headers=headers)

    if response == {}:
        return {}
    else:
        return dict(response.json())

def get_cities():
    cities = []
    offset = 0
    while True:
        loc_params = {'datasetid':'GHCND','locationcategoryid':'CITY','limit':'1000','offset':str(offset)}
        loc_batch = query_api(cat='locations',params=loc_params)
        if 'results'  in loc_batch.keys():
            cities += loc_batch['results']
            offset += 1000
        else:
            break
    return cities

def post(quote):
    client = Client(request=request)
    pw = os.environ.get('BSKY_CLIMATE_BOT_PW')
    if pw is None:
        print('no bsky account password found')
        exit()
    client.login('climate-bot.bsky.social', pw)

    text = ''
    client.send_post(text=text)

def main() -> None:
    #today = datetime.now()
    cities = get_cities()
    us_cities = [city for city in cities if city['id'].startswith('CITY:US')]
    print(len(us_cities))
    exit()

    data_params = {'datasetid':'GHCND',
                   'locationid':'ZIP:28801',
                   'startdate':'2010-05-01',
                   'enddate':'2010-05-01'}
    data = query_api('data',data_params)

if __name__ == '__main__':
    main()
