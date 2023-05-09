import folium


def plot_point(lat, lng):
    # Create map and display it
    fareo_map = folium.Map(location=[lat, lng], zoom_start=12)
    label = range(len(lat))
    folium.Marker([lat, lng], popup=label).add_to(fareo_map)
    incidents = folium.map.FeatureGroup()
    # add incidents to map
    fareo_map.add_child(incidents)
    # Display the map of Fareo
    fareo_map.save('fareo_map.html')


def map_init():
    # position of fareo island: 62, -6.783333
    # Create map and display it
    fareo_map = folium.Map(location=[62, -6.78], zoom_start=8)
    # label = range(len(lat))
    folium.Marker([62, -6.78]).add_to(fareo_map)
    incidents = folium.map.FeatureGroup()
    # add incidents to map
    fareo_map.add_child(incidents)
    # Display the map of Fareo
    fareo_map.save('fareo_map.html')
