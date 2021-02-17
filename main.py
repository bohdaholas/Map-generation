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



