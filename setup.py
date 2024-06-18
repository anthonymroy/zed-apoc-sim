import config
from data.list_of_contiguous_states import CONTIGUOUS_STATES
import geopandas as gpd
import os
import pandas as pd
from py_linq import Enumerable
import pygris
import requests
import utils

MODE_ERROR_MESSAGE = "MODE must be 'US' or the two-letter abbreviation of a state"

def download_shapefile(filename:str, mode:str) -> gpd.GeoDataFrame:
    match mode:
        case "US":
            gdf = download_state_shapefile(filename)            
        case _:
            gdf = download_county_shapefile(filename, mode)
    return gdf        

def download_state_shapefile(filename:str) -> gpd.GeoDataFrame:
    print(f"Can not find {filename}. Downloading now...")
    gdf = pygris.states()
    gdf.to_file(filename, )
    return gdf

def download_county_shapefile(filename:str, state) -> gpd.GeoDataFrame:
    print(f"Can not find {filename}. Downloading now...")
    gdf = pygris.counties(state=state)
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
                    "name":name2,
                    "border_length":shared_border_length,
                    "fraction": shared_border_length/my_border_length
                })
        data.append({
            "name": name1,
            "border_length": my_border_length,
            "neighbors": neighbors
        })
    utils.write_json_file(data, filepath)
    return pd.DataFrame.from_records(data, index="name")

def generate_populationfile(filename, mode) -> pd.DataFrame:
    print(f"Can not find {filename}. Downloading now...")
    if mode == "US":
        url = "https://api.census.gov/data/2019/pep/charagegroups?get=NAME,POP&HISP=0&for=state:*"
    elif mode in [state["short_name"] for state in CONTIGUOUS_STATES]:
        url = "https://api.census.gov/data/2019/pep/charagegroups?get=NAME,POP&HISP=0&for=county:*"
    else:
        raise ValueError(MODE_ERROR_MESSAGE)
    session = requests.Session()
    response = session.get(url)
    if response.status_code != 200:
        raise RuntimeError(response.reason)
    data = response.json()
    df = pd.DataFrame(data[1:], columns=data[0])
    df.set_index("NAME", inplace=True)
    # Convert to the proper types
    df["POP"] = pd.to_numeric(df["POP"])
    df["HISP"] = pd.Series(df["HISP"], dtype=pd.StringDtype)
    df["state"] = pd.Series(df["state"], dtype=pd.StringDtype)
    if "county" in df.keys():
        df["county"] = pd.Series(df["county"], dtype=pd.StringDtype)
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

def main(mode) -> tuple[gpd.GeoDataFrame, pd.DataFrame, pd.DataFrame]:

    shape_file = os.path.join(config.SHAPE_DIRECTORY,f"{mode}{config.BASE_BORDERS_FILENAME}")
    neighbors_pathfile = os.path.join(config.DATA_DIRECTORY,f"{mode}{config.BASE_NEIGHBORS_FILENAME}")

    if mode == "US":
        population_file = config.STATE_POPULATIONS_FILENAME
    elif mode in [state["short_name"] for state in CONTIGUOUS_STATES]:        
        population_file = config.COUNTY_POPULATIONS_FILENAME
    else:
        raise ValueError(MODE_ERROR_MESSAGE)
        
    if os.path.exists(shape_file):
        shape_gdf = gpd.read_file(shape_file)
    else:
        shape_gdf = download_shapefile(shape_file, mode)
    shape_gdf.set_index("NAME", inplace=True)

    if mode == "US":
        shape_gdf = filter_states_for_contiguous(shape_gdf)
    elif mode in [state["short_name"] for state in CONTIGUOUS_STATES]:
        shape_gdf = filter_counties_for_state(shape_gdf, mode, "STATEFP")
    else:
        raise ValueError(MODE_ERROR_MESSAGE)

    if os.path.exists(neighbors_pathfile):
        neighbors_df = utils.df_from_json(neighbors_pathfile, index="name")
    else:
        neighbors_df = generate_neighborfile(shape_gdf, neighbors_pathfile)    

    if os.path.exists(population_file):
        population_df = pd.read_csv(population_file, index_col="NAME")
        population_df["HISP"] = pd.Series(population_df["HISP"], dtype=pd.StringDtype)
        population_df["state"] = pd.Series(population_df["state"], dtype=pd.StringDtype)
        if "county" in population_df.keys():
            population_df["county"] = pd.Series(population_df["county"], dtype=pd.StringDtype)
    else:
        population_df = generate_populationfile(population_file, mode)
   
    if mode == "US":
        neighbors_df = filter_states_for_contiguous(neighbors_df)
        population_df = filter_states_for_contiguous(population_df)
    elif mode in [state["short_name"] for state in CONTIGUOUS_STATES]:
        population_df = filter_counties_for_state(population_df, mode, "state")
        population_df = rename_population_df(population_df, shape_gdf)
    else:
        raise ValueError(MODE_ERROR_MESSAGE)
    
    return (shape_gdf, neighbors_df, population_df)
        
if __name__ == "__main__":
    main("LA")