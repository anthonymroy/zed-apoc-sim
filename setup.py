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
    print(f"Can not find {filename}. Downloading now...")
    #Remove below for national-counties
    gdf = pygris.states(cb=True, resolution="500k")
    gdf.to_file(filename, )
    return gdf

def download_counties_shapefile(filename:str) -> gpd.GeoDataFrame:
    print(f"Can not find {filename}. Downloading now...")
    gdf = pygris.counties(cb=True, resolution="500k")
    gdf.to_file(filename, driver='ESRI Shapefile')
    return gdf

def generate_county_neighborfile(gdf:gpd.GeoDataFrame, neighbor_states_df:pd.DataFrame) -> pd.DataFrame:
    data = []
    for index in neighbor_states_df.index:
        print(f"Constructing county neighborhoods for {neighbor_states_df.at[index,'name']}") 
        my_state_fps = neighbor_states_df.at[index,"state_fp"]
        state_fps_to_keep = [my_state_fps]
        for neighbor in neighbor_states_df.at[index,"neighbors"]:
            state_fps_to_keep.append(neighbor["neighbor_state_fp"])
        filtered_gdf = gdf[gdf["STATEFP"].isin(state_fps_to_keep)]
        new_data = generate_neighborfile(filtered_gdf)
        for new_datum in new_data:
            if new_datum['state_fp'] == my_state_fps:
                data.append(new_datum)
    return data

def generate_neighborfile(gdf:gpd.GeoDataFrame) -> list[dict]:
    data = []
    for idx1 in gdf.index:
        neighbors = []        
        my_dict = {
            "id":gdf.at[idx1, "id"], 
            "state_fp":gdf.at[idx1, "STATEFP"],
            "name":gdf.at[idx1, "NAME"],
        }
        if "COUNTYFP" in gdf.columns:
            my_dict["county_fp"] = gdf.at[idx1, "COUNTYFP"]
        # Shapefile polygons are 1:100 km
        my_border_length = 100 * utils.get_border_length(gdf.geometry[idx1])
        my_dict["border_length"] = my_border_length
        for idx2 in gdf.index:
            if idx1 == idx2:
                continue
            # Shapefile polygons are 1:100 km
            shared_border_length = 100 * utils.get_shared_border_length(gdf.geometry[idx1],
                                                                         gdf.geometry[idx2])
            if shared_border_length > 0:
                neighbor_dict = {
                    "neighbor_id":gdf.at[idx2, "id"], 
                    "neighbor_state_fp":gdf.at[idx2, "STATEFP"],
                    "neighbor_name":gdf.at[idx2, "NAME"],
                    "shared_border_length":shared_border_length,
                }
                if "COUNTYFP" in gdf.columns:
                    neighbor_dict["county_fp"] = gdf.at[idx2, "COUNTYFP"]
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

# def filter_states_for_contiguous(src_df):
#     ret_df = src_df.copy()
#     to_keep = [state["name"] for state in CONTIGUOUS_STATES]
#     ret_df = ret_df[ret_df["STATE_NAME"].isin(to_keep)]
#     return ret_df

# def filter_counties_for_state(src_df, state_short_name, filter_key):
#     states = Enumerable(CONTIGUOUS_STATES)
#     state_to_keep = states.where(lambda s: s["short_name"] == state_short_name).single()
#     ret_df = src_df.drop(src_df[~(src_df[filter_key] == state_to_keep["state_fp"])].index)
#     return ret_df

# def rename_population_df(src_df:pd.DataFrame, gdf:gpd.GeoDataFrame):
#     ret_df = src_df.set_index("county", inplace=False)
#     my_gdf = gdf.reset_index(inplace=False)
#     my_gdf.set_index("COUNTYFP", inplace=True)
#     ret_df["NAME"] = my_gdf["NAME"]
#     ret_df.reset_index(inplace=True)
#     ret_df.set_index("NAME", inplace=True)
#     return ret_df

def consolidate_populations(county_pop_df:pd.DataFrame) -> pd.DataFrame:
    

def main(settings:Settings, filepaths:Filepaths) -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame, pd.DataFrame, pd.DataFrame]:    
    state_shape_filepath = os.path.join(filepaths.shape_directory,filepaths.state_shapefile_filename)
    state_neighbors_filepath = os.path.join(filepaths.neighbor_directory,filepaths.state_neighbors_filename)
    counties_shape_filepath = os.path.join(filepaths.shape_directory,filepaths.county_shapefile_filename)
    county_neighbors_filepath = os.path.join(filepaths.neighbor_directory,filepaths.county_neighbors_filename)
    population_filepath = filepaths.county_populations_filename
    
    if os.path.exists(state_shape_filepath):
        state_shape_gdf = gpd.read_file(state_shape_filepath)
    else:
        state_shape_gdf = download_states_shapefile(state_shape_filepath)   
    state_shape_gdf["id"] = state_shape_gdf["STATEFP"]
    state_shape_gdf = sch.clean_df(state_shape_gdf, sch.ShapeSchema)
    state_shape_gdf = filter_for_contiguous(state_shape_gdf)

    if settings.simulation_level[0].lower() == "county":
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

    if os.path.exists(state_neighbors_filepath):  
        print(f"Downloading {state_neighbors_filepath}")      
        state_neighbors_df = utils.df_from_json(state_neighbors_filepath)
    else:
        print(f"Can not find {state_neighbors_filepath}. Generating now...")
        state_neighbors_data = generate_neighborfile(state_shape_gdf)
        utils.write_json_file(state_neighbors_data, state_neighbors_filepath)  
        state_neighbors_df = pd.DataFrame.from_records(state_neighbors_data)
    state_neighbors_df = sch.clean_df(state_neighbors_df, sch.GraphSchema)    

    if os.path.exists(county_neighbors_filepath):
        print(f"Downloading {county_neighbors_filepath}")  
        county_neighbors_df = utils.df_from_json(county_neighbors_filepath)
    else:
        print(f"Can not find {county_neighbors_filepath}. Generating now...")
        county_neighbors_data = generate_county_neighborfile(counties_shape_gdf, state_neighbors_df) 
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

    match settings.simulation_level[0].lower():    
        case "state":
            simulation_gdf = state_shape_gdf
            neighbor_df = state_neighbors_df
            population_df = consolidate_populations(county_population_df)
        case "county":
            simulation_gdf = counties_shape_gdf
            neighbor_df = county_neighbors_df
            population_df = county_population_df

    simulation_gdf.set_index("id", inplace=True)
    neighbor_df.set_index("id", inplace=True)
    population_df.set_index("id", inplace=True)
    return (state_shape_gdf, simulation_gdf, neighbor_df, population_df)
        
if __name__ == "__main__":
    my_filepaths = Filepaths()
    my_settings = Settings()
    main(my_settings, my_filepaths)