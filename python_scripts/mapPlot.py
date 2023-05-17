import folium
from folium.plugins import Draw, MousePosition


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
    # allow the drawing tool, but rectangle only, others are all False
    draw = Draw(
        export=True,
        position='topleft',
        draw_options={'polyline': False,
                      'circlemarker': False,
                      'marker': False,
                      'circle': False,
                      'polygon': False},
        edit_options={'poly': {'allowIntersection': False}}
    )
    draw.add_to(fareo_map)
    # monitor the move of mouse and display the real time position
    MousePosition(
        position="topright",
        separator=" | Lng: ",
        empty_string="NaN",
        num_digits=10,
        prefix="Lat: ",
    ).add_to(fareo_map)
    # save the map of Fareo
    fareo_map.save('fareo_map.html')
    return fareo_map
