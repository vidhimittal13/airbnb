
import pandas as pd
import itertools
import sys
import folium
import numpy as np

#Read-in data
data = pd.read_csv("listings.csv")
#Remove listings not in NY
data = data[data['host_location'].str.contains('New York', na=False)]
#Extract relevant attributes
data = data[["id", "listing_url", "latitude", "longitude", "neighbourhood_group_cleansed"]]
#Remove duplicates
data = data.drop_duplicates()
#Remove listings w/o location data
data = data.dropna(subset=['id', 'latitude', 'longitude'])

#Set coordinates of NYC
north = 40.92
south = 40.4
east = -73.6
west = -74

data = data[(data['latitude'] >= south) 
            & (data['latitude'] <= north) 
            & (data['longitude'] >= west) 
            & (data['longitude'] <= east)]

# def create_point(row):
#     return (row['latitude'], row['longitude'])

# # Apply function to create tuple column
# data['Lat-Lon'] = data.apply(create_point, axis=1)


data.to_csv("new_listings.csv")


