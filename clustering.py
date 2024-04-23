from sklearn.cluster import DBSCAN
from math import radians, cos, sin, sqrt, atan2
import numpy as np
import pandas as pd
import folium
import matplotlib.pyplot as plt
from sklearn.neighbors import NearestNeighbors
import numpy as np


crimes = pd.read_csv("NY_arrests.csv")
listing = pd.read_csv("new_listings.csv")

crime_data = list(zip(crimes['Latitude'], crimes['Longitude']))
listing_location = list(zip(listing['latitude'], listing['longitude']))

k = 150
r = 20
# Initialize KNN model
knn = NearestNeighbors(n_neighbors=k, radius = r, metric='haversine')

# Fit KNN model with crime locations
knn.fit(crime_data)

# # Find nearest neighbors for each Airbnb location
indices = knn.kneighbors(listing_location, return_distance=False)

# # Filter results to include only crimes within a 10-mile radius
crime_within_radius = []

for airbnb_index, crime_indices in enumerate(indices):
    crime_within_radius.append(crimes.iloc[crime_indices][['ARREST_KEY','OFNS_DESC','Latitude', 'Longitude', 'offense_level']])


safety_scores = []

# Iterate over each crime incident DataFrame in crime_within_radius
for crime_df in crime_within_radius:
    # Extract offense levels of the nearest crimes
    offense_levels = crime_df['offense_level']
    
    # Calculate the average offense level
    if len(offense_levels) > 0:
        avg_offense_level = offense_levels.mean()
    else:
        avg_offense_level = None
    
    # Append the calculated average to the safety_scores list
    safety_scores.append(avg_offense_level)

# Assign the 
# safety scores to the 'safety_score' column in the listing DataFrame
listing['safety_score'] = safety_scores

map_center = [40.7128, -74.0060]
mymap = folium.Map(location=map_center, zoom_start=12)

# Define a color scale for safety scores
def color_scale(score):
    if score is None:
        return 'gray'  # Assign gray color to None values
    elif score >= 4:
        return 'red'  # Red for scores of 4 or above
    elif score >= 3.5:
        return 'orange'  # Dark orange for scores between 3.5 and 4 (exclusive)
    elif score >= 3:
        return 'darkgreen'  # Orange for scores between 3 and 3.5 (exclusive)
    elif score >= 2.5:
        return 'lightgreen'  # Gold for scores between 2.5 and 3 (exclusive)
    elif score >= 2:
        return 'blue'  # Yellow-green for scores between 2 and 2.5 (exclusive)
    else:
        return 'lightblue'  # Lime green for scores below 2
sample_listings = listing.iloc[0:5000]
# Iterate over each listing and its safety score

legend_html = '''
    <div style="position: fixed; bottom: 50px; left: 50px; width: 200px; height: 200px; 
    background-color: rgba(255, 255, 255, 0.8); border-radius: 5px; z-index:9999; font-size:14px;
    ">
    &nbsp; <b>Safety Score</b> <br>
    &nbsp; 4+ <i class="fa fa-map-marker fa-2x" style="color:red"></i><br>
    &nbsp; 3.5 - 4 <i class="fa fa-map-marker fa-2x" style="color:orange"></i><br>
    &nbsp; 3 - 3.5 <i class="fa fa-map-marker fa-2x" style="color:darkgreen"></i><br>
    &nbsp; 2.5 - 3 <i class="fa fa-map-marker fa-2x" style="color:lightgreen"></i><br>
    &nbsp; 2 - 2.5 <i class="fa fa-map-marker fa-2x" style="color:blue"></i><br>
    &nbsp; Below 2 <i class="fa fa-map-marker fa-2x" style="color:lightblue"></i><br>
    </div>
    '''
mymap.get_root().html.add_child(folium.Element(legend_html))



for i, row in sample_listings.iterrows():
    # Get the safety score of the listing
    safety_score = row['safety_score']
    

    # Determine the color for the marker based on the safety score
    marker_color = color_scale(safety_score)
    

    # Create a Marker object with custom icon
    folium.Marker(location=[row['latitude'], row['longitude']],
                  icon=folium.Icon(color=marker_color),
                  popup=f"Safety Score: {safety_score}, Listing: {row['listing_url']}").add_to(mymap)
mymap.save("safety_map.html")

