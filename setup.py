import config
from data.list_of_contiguous_states import CONTIGUOUS_STATES
import data.schema as sch
import geopandas as gpd
import os
import pandas as pd
from py_linq import Enumerable
import pygris
import requests
import utils

REGION_ERROR_MESSAGE = "Region must be 'US' or the two-letter abbreviation of a state"

def download_shapefile(filename:str, region_text:str) -> gpd.GeoDataFrame:
    match region_text:
        case "US":
            gdf = download_state_shapefile(filename)            
        case _:
            gdf = download_county_shapefile(filename, region_text)
    return gdf        

def download_state_shapefile(filename:str) -> gpd.GeoDataFrame:
    print(f"Can not find {filename}. Downloading now...")
    gdf = pygris.states(cb=True, resolution="500k")
    gdf.to_file(filename, )
    return gdf

def download_county_shapefile(filename:str, state) -> gpd.GeoDataFrame:
    print(f"Can not find {filename}. Downloading now...")
    gdf = pygris.counties(state=state, cb=True, resolution="500k")
    gdf.to_file(filename, driver='ESRI Shapefile')
    return gdf

# TODO - Improve loop below by testing for name1 >- name2 instead of ==
def generate_neighborfile(gdf:gpd.GeoDataFrame, filepath:str) -> pd.DataFrame:
    print(f"Can not find {filepath}. Generating now...")
    data = []
    for name1 in gdf.index:        
        neighbors = []
        my_border_length = utils.get_border_length(gdf.geometry[name1])
        for name2 in gdf.index:
            if name1 == name2:
                continue
            shared_border_length = utils.get_shared_border_length(gdf.geometry[name1], gdf.geometry[name2])
            if shared_border_length > 0:
                neighbors.append({
                    "neighbor_name":name2,
                    "shared_border_length":shared_border_length,
                    "fraction": shared_border_length/my_border_length
                })
        data.append({
            "name": name1,
            "border_length": my_border_length,
            "neighbors": neighbors
        })
    utils.write_json_file(data, filepath)
    return pd.DataFrame.from_records(data, index="name")

def add_leading_zeros(value:any, desired_length=3) -> str:
    text = str(value)
    while(len(text) < desired_length):
        text = "0"+text
    return text

def generate_populationfile(filename, region_text) -> pd.DataFrame:
    print(f"Can not find {filename}. Downloading now...")
    if region_text == "US":
        url = "https://api.census.gov/data/2019/pep/charagegroups?get=NAME,POP&HISP=0&for=state:*"
    elif region_text in [state["short_name"] for state in CONTIGUOUS_STATES]:
        url = "https://api.census.gov/data/2019/pep/charagegroups?get=NAME,POP&HISP=0&for=county:*"
    else:
        raise ValueError(REGION_ERROR_MESSAGE)
    session = requests.Session()
    response = session.get(url)
    if response.status_code != 200:
        raise RuntimeError(response.reason)
    data = response.json()
    df = pd.DataFrame(data[1:], columns=data[0])
    df.set_index("NAME", inplace=True)
    df.to_csv(filename)
    return df    

def filter_states_for_contiguous(src_df):
    ret_df = src_df.copy()
    to_keep = [state["name"] for state in CONTIGUOUS_STATES]
    ret_df = ret_df[ret_df.index.isin(to_keep)]
    return ret_df

def filter_counties_for_state(src_df, state_short_name, filter_key):
    states = Enumerable(CONTIGUOUS_STATES)
    state_to_keep = states.where(lambda s: s["short_name"] == state_short_name).single()
    ret_df = src_df.drop(src_df[~(src_df[filter_key] == state_to_keep["state_fp"])].index)
    return ret_df

def rename_population_df(src_df:pd.DataFrame, gdf:gpd.GeoDataFrame):
    ret_df = src_df.set_index("county", inplace=False)
    my_gdf = gdf.reset_index(inplace=False)
    my_gdf.set_index("COUNTYFP", inplace=True)
    ret_df["NAME"] = my_gdf["NAME"]
    ret_df.reset_index(inplace=True)
    ret_df.set_index("NAME", inplace=True)
    return ret_df

def main(region) -> tuple[gpd.GeoDataFrame, pd.DataFrame, pd.DataFrame]:

    shape_file = os.path.join(config.SHAPE_DIRECTORY,f"{region}{config.SHAPEFILE_FILENAME_SUFFIX}")
    neighbors_pathfile = os.path.join(config.NEIGHBOR_DIRECTORY,f"{region}{config.NEIGHBORS_FILENAME_SUFFIX}")

    if region == "US":
        population_file = config.STATE_POPULATIONS_FILENAME
    elif region in [state["short_name"] for state in CONTIGUOUS_STATES]:        
        population_file = config.COUNTY_POPULATIONS_FILENAME
    else:
        raise ValueError(REGION_ERROR_MESSAGE)
        
    if os.path.exists(shape_file):
        shape_gdf = gpd.read_file(shape_file)
    else:
        shape_gdf = download_shapefile(shape_file, region)    
    shape_gdf.set_index("NAME", inplace=True)
    shape_gdf = sch.clean_df(shape_gdf, sch.ShapeSchema)

    if region == "US":
        shape_gdf = filter_states_for_contiguous(shape_gdf)
    elif region in [state["short_name"] for state in CONTIGUOUS_STATES]:
        shape_gdf = filter_counties_for_state(shape_gdf, region, "STATEFP")
    else:
        raise ValueError(REGION_ERROR_MESSAGE)

    if os.path.exists(neighbors_pathfile):
        neighbors_df = utils.df_from_json(neighbors_pathfile, index="name")
    else:
        neighbors_df = generate_neighborfile(shape_gdf, neighbors_pathfile)       
    neighbors_df = sch.clean_df(neighbors_df, sch.GraphSchema)

    if os.path.exists(population_file):
        population_df = pd.read_csv(population_file, index_col="NAME")
    else:
        population_df = generate_populationfile(population_file, region)
    population_df = sch.clean_df(population_df, sch.PopulationSchema)
    #population_df["state"] = population_df["state"].apply(add_leading_zeros, 2)
    #if "county" in population_df.keys():
            #population_df["county"] = population_df["county"].apply(add_leading_zeros, 3)

    if region == "US":
        neighbors_df = filter_states_for_contiguous(neighbors_df)
        population_df = filter_states_for_contiguous(population_df)
    elif region in [state["short_name"] for state in CONTIGUOUS_STATES]:
        population_df = filter_counties_for_state(population_df, region, "state")        
        population_df = rename_population_df(population_df, shape_gdf)
    else:
        raise ValueError(REGION_ERROR_MESSAGE)    
    
    return (shape_gdf, neighbors_df, population_df)
        
if __name__ == "__main__":
    main("CA")