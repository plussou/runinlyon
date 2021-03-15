
import requests
import datetime
import pandas as pd

BASE_URI = "https://www.metaweather.com"

def get_lat_lon(adresse):
    url="https://api-adresse.data.gouv.fr/search/"
    params={'q':adresse}
    response=requests.get(url,params=params).json()
    lon, lat = response['features'][0]['geometry']['coordinates']
    return (lat,lon)

def get_woeid(lat,lon):
    url = BASE_URI + f"/api/location/search/"
    params = {'lattlong':f'{lat},{lon}'}
    response = requests.get(url,params=params).json()
    return response[0]

def new_datedatetime(row):
    date=row[0].date()
    time = row[1].time().replace(microsecond=0)
    return datetime.datetime.combine(date,time)

def get_temperature_one_day(woeid,year,month,day):
    date_str = datetime.date(year,month,day).__str__().replace('-','/')
    woeid_plus_date=str(woeid)+'/'+date_str
    url = BASE_URI + f"/api/location/{woeid_plus_date}/"
    response = requests.get(url).json()
    temp_list=[[record['created'],record['applicable_date'],record['min_temp'],\
                record['max_temp'],record['the_temp']] for record in response]
    return pd.DataFrame(temp_list,columns=['created','applicable_date','min_temp','max_temp','the_temp'])

def get_temperature_many_days(woeid,year_1,month_1,day_1,year_2,month_2,day_2):
    date_1 = datetime.date(year_1,month_1,day_1)
    date_2 = datetime.date(year_2,month_2,day_2)
    table = pd.DataFrame()
    for day in range((date_2 - date_1).days+1):
        date = date_1 + datetime.timedelta(day)
        year = int(date.year)
        month = int(date.month)
        day = int(date.day)
        table = pd.concat([table,get_temperature_one_day(woeid,year,month,day)],ignore_index=True)

    table['date']=pd.to_datetime(table['applicable_date'])
    table['time']=pd.to_datetime(table['created'])
    table.drop(columns=['created','applicable_date'],inplace=True)
    table['new_date'] = table[['date','time']].apply(new_datedatetime,axis=1)
    table.sort_values(by='new_date',inplace=True)
    table.set_index('new_date',drop=True,inplace=True)
    table.drop(columns=['date','time'],inplace=True)

    return table
