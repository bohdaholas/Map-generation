import re
import folium
from geopy.geocoders import Nominatim
from haversine import haversine


def get_movie_data_from_file(file_path: str, year: str) -> dict:
    """
    Get movie data from file in the following form:
    {movie_name: (latitude, longitude), ...}
    """
    movies_data = {}
    movie_name_pattern = re.compile(r'".+"')
    movie_year_pattern = re.compile(r'\(\d{4}\)')
    place_pattern = re.compile(r'\B\t(\w+)\n')
    nom = Nominatim(user_agent="map-generation")
    with open(file_path) as file:
        for line in file:
            movie_name = movie_name_pattern.match(line)
            movie_year = movie_year_pattern.search(line)
            place = place_pattern.search(line)
            if movie_year and year in movie_year.group() and movie_name and \
                    movie_name.group() not in movies_data and place:
                location = nom.geocode(place.group(1))
                if location is not None:
                    movies_data[movie_name.group()] = location.latitude, location.longitude
    return movies_data


def sort_by_distance(unsorted_movies_data: dict) -> dict:
    """
    Sort movie filming locations according to user's given location
    """
    sorted_movies_data = dict(sorted(unsorted_movies_data.items(),
                                     key=lambda movie_data: haversine(user_location, movie_data[1])))
    return sorted_movies_data


def build_map(movie_sample: dict) -> None:
    """
    Build a folium map and save it as an HTML file
    """
    folium_map = folium.Map()
    for idx, map_movie in enumerate(movie_sample.items()):
        if idx < 10:
            folium.Marker(location=[*map_movie[1]], popup=map_movie[0]).add_to(folium_map)
    tile_layers = 'Open Street Map', 'Stamen Terrain', 'Stamen Toner', \
                  'Stamen Watercolor', 'CartoDB Positron', 'CartoDB Dark_Matter'
    for tile_layer in tile_layers:
        folium.raster_layers.TileLayer(tile_layer).add_to(folium_map)
    folium_map.add_child(folium.LayerControl())
    folium_map.save(f"{user_year}.html")


if __name__ == '__main__':
    user_year = input("Please enter a year you would like to have a map for: \n")
    user_location = tuple((int(coordinate) for coordinate
                           in input("Please enter your location (format: lat, long): \n").split(',')))
    sorted_movie_sample = sort_by_distance(get_movie_data_from_file('locations.list', user_year))
    build_map(sorted_movie_sample)
    print(sorted_movie_sample)
