import folium
import pandas as pd
import geopandas as gpd
import numpy as np
import requests
import io
from folium.plugins import MarkerCluster
from shapely.geometry import Point

# Load the datasets
demand_points = pd.read_csv("Demand_points.csv")
warehouse_points = pd.read_csv("Warehouse_points.csv")
selected_warehouses = pd.read_csv("Selected_Warehouses.csv")
demand_allocations = pd.read_csv("Demand_Allocations.csv")

# Load India district boundaries
india_district_url = "https://raw.githubusercontent.com/geohacker/india/master/district/india_district.geojson"
response = requests.get(india_district_url)
india_districts = gpd.read_file(io.StringIO(response.text))

# Create a GeoDataFrame for demand points
geometry = [Point(xy) for xy in zip(demand_points['longitude'], demand_points['latitude'])]
demand_gdf = gpd.GeoDataFrame(demand_points, geometry=geometry, crs="EPSG:4326")

# Filter demand points to only include those within India
india_boundary = india_districts.unary_union
demand_gdf['in_india'] = demand_gdf.geometry.apply(lambda x: india_boundary.contains(x))
demand_gdf = demand_gdf[demand_gdf['in_india']]

# Create a base map centered on India
m = folium.Map(location=[20.5937, 78.9629], zoom_start=5, tiles='cartodbpositron')


# Add a colormap for demand intensity
def get_color(demand):
    # Create a color gradient from light blue to dark blue based on demand
    norm_demand = np.clip(demand / demand_gdf['Demand'].max(), 0.1, 1)
    return f'#{int(255 - 200 * norm_demand):02x}{int(255 - 150 * norm_demand):02x}ff'


# Add demand points with varying blue shades based on demand
for idx, row in demand_gdf.iterrows():
    folium.CircleMarker(
        location=[row['latitude'], row['longitude']],
        radius=5,
        color=get_color(row['Demand']),
        fill=True,
        fill_color=get_color(row['Demand']),
        fill_opacity=0.7,
        popup=f"Pincode: {row['pincode']}<br>Demand: {row['Demand']}"
    ).add_to(m)

# Add potential warehouse candidates as hollow red circles
for idx, row in warehouse_points.iterrows():
    folium.CircleMarker(
        location=[row['Latitude'], row['Longitude']],
        radius=8,
        color='red',
        fill=False,
        weight=2,
        popup=f"Potential Warehouse: {row['district']}<br>Total Demand: {row['TotalDemand']}"
    ).add_to(m)

# Add selected warehouses as solid red dots
for idx, row in selected_warehouses.iterrows():
    # Find this warehouse in the warehouse_points dataframe
    warehouse_info = warehouse_points[warehouse_points['district'] == row['Warehouse']]

    if not warehouse_info.empty:
        folium.CircleMarker(
            location=[warehouse_info.iloc[0]['Latitude'], warehouse_info.iloc[0]['Longitude']],
            radius=10,
            color='red',
            fill=True,
            fill_color='red',
            fill_opacity=0.7,
            popup=f"Selected Warehouse: {row['Warehouse']}"
        ).add_to(m)

# Create a dictionary to store warehouse locations
warehouse_locations = {}
for idx, row in warehouse_points.iterrows():
    warehouse_locations[row['district']] = (row['Latitude'], row['Longitude'])

# Add dotted violet lines connecting warehouses to their allocated demand points
for idx, row in demand_allocations.iterrows():
    # Find the demand point
    demand_point = demand_gdf[demand_gdf['pincode'] == row['Pincode']]

    if not demand_point.empty and row['Warehouse'] in warehouse_locations:
        warehouse_loc = warehouse_locations[row['Warehouse']]
        demand_loc = (demand_point.iloc[0]['latitude'], demand_point.iloc[0]['longitude'])

        folium.PolyLine(
            locations=[warehouse_loc, demand_loc],
            color='purple',
            weight=1,
            opacity=0.6,
            dash_array='5, 5',
            popup=f"Distance: {row['Distance']:.2f} km<br>Weighted Cost: {row['WeightedCost']:.2f}"
        ).add_to(m)

# Add legend
legend_html = '''
<div style="position: fixed; 
            bottom: 50px; right: 50px; width: 180px; height: 120px; 
            border: 2px solid grey; z-index: 9999; 
            background-color: white;
            padding: 10px;
            font-size: 14px;
            ">
    <p><svg height="12" width="12"><circle cx="6" cy="6" r="5" fill="blue" opacity="0.7"/></svg> Demand Points</p>
    <p><svg height="12" width="12"><circle cx="6" cy="6" r="5" stroke="red" stroke-width="2" fill="none"/></svg> Potential Warehouses</p>
    <p><svg height="12" width="12"><circle cx="6" cy="6" r="5" fill="red" opacity="0.7"/></svg> Selected Warehouses</p>
    <p><svg height="12" width="36"><line x1="2" y1="6" x2="34" y2="6" stroke="purple" stroke-width="2" stroke-dasharray="5,5"/></svg> Allocations</p>
</div>
'''
m.get_root().html.add_child(folium.Element(legend_html))

# Save the map to an HTML file
m.save('warehouse_optimization_map.html')

# Display the map if in a notebook environment
m