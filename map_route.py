import folium
import pandas as pd
import webbrowser, os
from here import HereAPI
from instance import APP_ID, APP_CODE


here = HereAPI(APP_ID=APP_ID,APP_CODE=APP_CODE)
data = pd.DataFrame(here.seed_points())
data['lat'] = [float(i) for i in data['lat']]
data['lon'] = [float(i) for i in data['lon']]
data['names'] = ['Base', 'Cascais', 'Oeiras', 'Paco_darcos', 'Queijas', 'Carnaxide', 
                'Restelo', 'Campolide', 'Rossio', 'Cais_do_sodre']
data = data.reset_index()

class MapRoute:
    def __init__(self, route):
        self.points = route.points

    def __repr__(self):
        return "<MapRoute({})>".format(self.points)

    def order_data_points(self):
        self.data = pd.DataFrame()
        for point in self.points:
            self.data = self.data.append(data[data['index']==point])

    def map_points(self, filename='map.html'):
        self.order_data_points()
        my_map = folium.Map(location=[self.data['lat'].mean(), self.data['lon'].mean()], zoom_start=12)
        
        points_group = folium.FeatureGroup(name='Points')
        line_group = folium.FeatureGroup(name='Lines')

        icon_html = """
            <div style="background-color: navy; color:white; text-align:center; border-radius: 5px;">{}
            </div>
        """

        for i, lat, lon, name in zip(self.data['index'], self.data['lat'], self.data['lon'], self.data['names']):
            points_group.add_child(folium.Marker(location=[lat, lon], popup=folium.Popup(name), 
                        icon=folium.DivIcon(icon_html.format(i))))

        line_group.add_child(folium.PolyLine(locations=list(zip(self.data['lat'][:2],self.data['lon'][:2])), weight=5, color='red'))
        line_group.add_child(folium.PolyLine(locations=list(zip(self.data['lat'][1:],self.data['lon'][1:])), weight=5))
            
        my_map.add_child(points_group)
        my_map.add_child(line_group)
        my_map.save(filename)
        webbrowser.open('file://' + os.path.realpath(filename))
        
    
if __name__ == "__main__":
    from basic_ga import Route
    my_map = MapRoute(Route(points=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0]))
    my_map.map_points()

    


