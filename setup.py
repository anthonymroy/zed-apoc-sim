from config import Filepaths, Settings
from data.list_of_contiguous_states import CONTIGUOUS_STATES
import data.schema as sch
import geopandas as gpd
import os
import pandas as pd
import pygris
import requests
import utils

def download_states_shapefile(filename:str) -> gpd.GeoDataFrame:
    #Remove below for national-counties
    gdf = pygris.states(cb=True, resolution="500k")
    gdf.to_file(filename, )
    return gdf

def download_counties_shapefile(filename:str) -> gpd.GeoDataFrame:
    gdf = pygris.counties(cb=True, resolution="500k")
    gdf.to_file(filename, driver='ESRI Shapefile')
    return gdf

def generate_neighborfile(gdf_src:gpd.GeoDataFrame) -> list[dict]:
    gdf = gdf_src.copy()
    gdf.set_index("id", inplace=True)
    buffer_gdf = gdf.to_crs(epsg=32618) #32618 is the UTM code for North America
    buffer_gdf['geometry'] = buffer_gdf.buffer(0.01) #1 km because polygons are 1:100 km

    # Self join based on intersection
    joined_gdf = buffer_gdf.sjoin(buffer_gdf, how='inner', predicate='intersects')

    # Filter out self-adjacencies
    neighbor_gdf = joined_gdf[joined_gdf.index != joined_gdf["index_right"]]

    data = []
    region_ids = neighbor_gdf.index.unique()
    for id1 in region_ids:
        neighbors = []
        my_dict = {
            "id":id1, 
            "state_fp":gdf.at[id1, "STATEFP"],
            "name":gdf.at[id1, "NAME"],
        }
        if "COUNTYFP" in gdf.columns:
            my_dict["county_fp"] = gdf.at[id1, "COUNTYFP"]
        # Shapefile polygons are 1:100 km
        my_border_length = 100 * utils.get_border_length(gdf.geometry[id1])
        my_dict["border_length"] = my_border_length
        neighbor_ids = neighbor_gdf[neighbor_gdf.index==id1]["index_right"]
        for id2 in neighbor_ids:
            # Shapefile polygons are 1:100 km
            shared_border_length = 100 * utils.get_shared_border_length(gdf.geometry[id1], gdf.geometry[id2])
            if shared_border_length > 0:
                neighbor_dict = {
                    "neighbor_id":id2, 
                    "neighbor_state_fp":gdf.at[id2, "STATEFP"],
                    "neighbor_name":gdf.at[id2, "NAME"],
                    "shared_border_length":shared_border_length,
                }
                if "COUNTYFP" in gdf.columns:
                    neighbor_dict["neighbor_county_fp"] = gdf.at[id2, "COUNTYFP"]
                neighbors.append(neighbor_dict)
        my_dict["neighbors"] = neighbors
        data.append(my_dict) 
    return data

def add_leading_zeros(value:any, desired_length=3) -> str:
    text = str(value)
    while(len(text) < desired_length):
        text = "0"+text
    return text

def generate_populationfile(filename) -> pd.DataFrame:
    print(f"Can not find {filename}. Downloading now...")
    url = "https://api.census.gov/data/2019/pep/charagegroups?get=NAME,POP&HISP=0&for=county:*"
    session = requests.Session()
    response = session.get(url)
    if response.status_code != 200:
        raise RuntimeError(response.reason)
    data = response.json()
    df = pd.DataFrame(data[1:], columns=data[0])    
    return df    

def filter_for_contiguous(src_df):
    ret_df = src_df.copy()
    to_keep = [add_leading_zeros(state["state_fp"], 2) for state in CONTIGUOUS_STATES]
    ret_df = ret_df[ret_df["STATEFP"].isin(to_keep)]
    return ret_df

def consolidate_populations(county_pop_df:pd.DataFrame) -> pd.DataFrame:
    state_data = []
    for state in CONTIGUOUS_STATES:
        state_fp = add_leading_zeros(state["state_fp"], 2)
        fliltered_county_pop_df = county_pop_df[county_pop_df["state"] == state_fp]
        pop = sum(fliltered_county_pop_df["POP"])
        state_data.append({
            "NAME":state["name"],
            "POP":pop,
            "state":state_fp,
            "id":state_fp
        })
    state_df = pd.DataFrame.from_records(state_data)
    return state_df

def get_states_shapefile(filepaths:Filepaths) -> gpd.GeoDataFrame:
    state_shape_filepath = os.path.join(filepaths.shape_directory,filepaths.state_shapefile_filename)
    if os.path.exists(state_shape_filepath):
        print(f"Downloading {state_shape_filepath}")
        state_shape_gdf = gpd.read_file(state_shape_filepath)
    else:
        print(f"Can not find {state_shape_filepath}. Generating now...")
        state_shape_gdf = download_states_shapefile(state_shape_filepath)   
    state_shape_gdf["id"] = state_shape_gdf["STATEFP"]
    state_shape_gdf = sch.clean_df(state_shape_gdf, sch.ShapeSchema)
    state_shape_gdf = filter_for_contiguous(state_shape_gdf)
    return state_shape_gdf

def get_county_shapefile(filepaths:Filepaths) -> gpd.GeoDataFrame:
    counties_shape_filepath = os.path.join(filepaths.shape_directory,filepaths.county_shapefile_filename)
    if os.path.exists(counties_shape_filepath):
            print(f"Downloading {counties_shape_filepath}")
            counties_shape_gdf = gpd.read_file(counties_shape_filepath)
    else:
        print(f"Can not find {counties_shape_filepath}. Generating now...")
        counties_shape_gdf = download_counties_shapefile(counties_shape_filepath)  
    counties_shape_gdf["STATEFP"] = counties_shape_gdf["STATEFP"].apply(add_leading_zeros, args=(2,))
    counties_shape_gdf["id"] = counties_shape_gdf["STATEFP"] + counties_shape_gdf["COUNTYFP"]
    counties_shape_gdf = sch.clean_df(counties_shape_gdf, sch.ShapeSchema)
    counties_shape_gdf = filter_for_contiguous(counties_shape_gdf)    
    return counties_shape_gdf

def main(settings:Settings, filepaths:Filepaths) -> tuple[gpd.GeoDataFrame, pd.DataFrame, pd.DataFrame]:  
    state_neighbors_filepath = os.path.join(filepaths.neighbor_directory,filepaths.state_neighbors_filename)
    
    county_neighbors_filepath = os.path.join(filepaths.neighbor_directory,filepaths.county_neighbors_filename)
    population_filepath = filepaths.county_populations_filename
    
    if settings.simulation_resolution.lower() == "state": 
        state_shape_gdf = get_states_shapefile(filepaths)
        if os.path.exists(state_neighbors_filepath):  
            print(f"Downloading {state_neighbors_filepath}")      
            state_neighbors_df = utils.df_from_json(state_neighbors_filepath)
        else:
            print(f"Can not find {state_neighbors_filepath}. Generating now...")
            state_neighbors_data = generate_neighborfile(state_shape_gdf)
            utils.write_json_file(state_neighbors_data, state_neighbors_filepath)  
            state_neighbors_df = pd.DataFrame.from_records(state_neighbors_data)
        state_neighbors_df = sch.clean_df(state_neighbors_df, sch.GraphSchema)    

    if settings.simulation_resolution.lower() == "county":        
        counties_shape_gdf = get_county_shapefile(filepaths)    
        if os.path.exists(county_neighbors_filepath):
            print(f"Downloading {county_neighbors_filepath}")  
            county_neighbors_df = utils.df_from_json(county_neighbors_filepath)
        else:
            print(f"Can not find {county_neighbors_filepath}. Generating now...")
            county_neighbors_data = generate_neighborfile(counties_shape_gdf) 
            utils.write_json_file(county_neighbors_data, county_neighbors_filepath)
            county_neighbors_df = pd.DataFrame.from_records(county_neighbors_data)     
        county_neighbors_df = sch.clean_df(county_neighbors_df, sch.GraphSchema)

    if os.path.exists(population_filepath):
        print(f"Downloading {population_filepath}")
        county_population_df = pd.read_csv(population_filepath)
    else:
        print(f"Can not find {population_filepath}. Generating now...")
        county_population_df = generate_populationfile(population_filepath)        
        county_population_df.to_csv(population_filepath)
    county_population_df["state"] = county_population_df["state"].apply(add_leading_zeros, args=(2,))
    county_population_df["county"] = county_population_df["county"].apply(add_leading_zeros, args=(3,))
    county_population_df["id"] = county_population_df["state"] + county_population_df["county"]
    county_population_df = sch.clean_df(county_population_df, sch.PopulationSchema)

    match settings.simulation_resolution.lower():    
        case "state":
            simulation_gdf = state_shape_gdf
            neighbor_df = state_neighbors_df
            population_df = consolidate_populations(county_population_df)
        case "county":
            simulation_gdf = counties_shape_gdf
            neighbor_df = county_neighbors_df
            population_df = county_population_df
        case _:
            raise ValueError("simulation_resolution must be 'state' or 'county'")

    simulation_gdf.set_index("id", inplace=True)
    neighbor_df.set_index("id", inplace=True)
    population_df.set_index("id", inplace=True)
    return (simulation_gdf, neighbor_df, population_df)
        
if __name__ == "__main__":
    my_filepaths = Filepaths()
    my_settings = Settings()
    my_settings.simulation_resolution = "state"
    df1, df2, df3, = main(my_settings, my_filepaths)   
    print(f"df1.shape = {df1.shape}") 
    print(f"df2.shape = {df2.shape}") 
    print(f"df3.shape = {df3.shape}") 
