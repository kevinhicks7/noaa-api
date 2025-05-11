import os
import requests

ncdc_api_key = os.environ.get('NOAA_API')
if ncdc_api_key is None:
    print('no api key found in environment variables')
    exit()
base_url = 'https://www.ncei.noaa.gov/cdo-web/api/v2/data?'
data_params = {'datasetid':'GHCND',
               'locationid':'ZIP:28801',
               'startdate':'2025-05-08',
               'enddate':'2025-05-08'}
filters = "&".join(f"{param}={val}" for param, val in data_params.items())
url = base_url + filters

headers = {'token': ncdc_api_key}
req = requests.get(url, headers=headers)
print(req.json())
