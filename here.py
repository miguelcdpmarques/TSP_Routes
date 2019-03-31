import numpy as np
import pandas as pd
from urllib import request
import json
from collections import namedtuple
from instance import APP_ID, APP_CODE


class HereAPI:

    def __init__(self, APP_ID, APP_CODE):
        self.config = {'APP_ID': APP_ID, 'APP_CODE': APP_CODE}
        self.Coordinates = namedtuple('Coordinates', ['lat', 'lon'])

    def calculate_route(self, waypoints, mode='fastest%3Btruck', departure='now'):
        # convert waypoints' list to string
        url = 'https://route.api.here.com/routing/7.2/calculateroute.json?app_id={}&app_code={}&{}&mode={}%3Btraffic%3Aenabled&departure={}'.format(self.config['APP_ID'], self.config['APP_CODE'], waypoints, mode, departure)
        json_obj = request.urlopen(url)
        data = json.load(json_obj)
        self.pprint(data['response'], indent=4)
        return data

    def calculate_matrix(self, points, mode='fastest%3Btruck', departure='now'):
        start_points, destination_points = self.format_points(points)
        url = 'https://matrix.route.api.here.com/routing/7.2/calculatematrix.json?app_id={}&app_code={}{}{}&mode={}&traffic=enabled&summaryattributes=tt,di,cf'.format(self.config['APP_ID'], self.config['APP_CODE'], start_points, destination_points, mode)
        # print(url)
        data = json.load(request.urlopen(url))['response']['matrixEntry']
        # self.pprint(data)
        for d in data: 
            d.update(d.pop('summary', {}))
        return pd.DataFrame(data)

    def pprint(self, json_data):
        print(json.dumps(json_data, indent=4))
    
    def format_points(self, points):
        start_points = ''
        destination_points = ''
        for i, point in enumerate(points):
            point_detail = str(i)+'='+point.lat+'%2C'+point.lon
            start_points += '&start' + point_detail
            destination_points += '&destination' + point_detail
        return start_points, destination_points

    def seed_points(self):
        base = self.Coordinates('38.7247', '-9.1623')
        cascais = self.Coordinates('38.6945', '-9.4313')
        oeiras = self.Coordinates('38.6869', '-9.3151')
        paco_darcos = self.Coordinates('38.7030', '-9.2995')
        queijas = self.Coordinates('38.7171','-9.2662')
        carnaxide = self.Coordinates('38.7238', '-9.2465')
        restelo = self.Coordinates('38.7084', '-9.2190')
        campolide = self.Coordinates('38.7310','-9.1703')
        rossio = self.Coordinates('38.7141','-9.1388')
        cais_do_sodre = self.Coordinates('38.7061','-9.1469')
        points = [base, cascais, oeiras, paco_darcos, queijas, carnaxide, 
                restelo, campolide, rossio, cais_do_sodre]
        return points

if __name__ == '__main__':
    here = HereAPI(APP_ID=APP_ID,APP_CODE=APP_CODE)
    points = here.seed_points()
    data = here.calculate_matrix(points=points)
    print(data)


