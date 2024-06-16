import config
from data.list_of_contiguous_states import CONTIGUOUS_STATES
import geopandas as gp
import os
import pandas as pd
import pygris
import requests
import utils

MODE_ERROR_MESSAGE = "MODE must be 'state' or 'county'"

def download_shapefile(filename:str, mode:str) -> gp.GeoDataFrame:
    match mode:
        case "state":
            gdf = download_state_shapefile(filename)
        case "county":
            gdf = download_county_shapefile(filename)
        case _:
            raise ValueError("mode must be 'state' or 'county'")
    return gdf        

def download_state_shapefile(filename:str) -> gp.GeoDataFrame:
    print(f"Can not find {filename}. Downloading now...")
    gdf = pygris.states()
    gdf.to_file(filename, )
    return gdf

def download_county_shapefile(filename:str) -> gp.GeoDataFrame:
    print(f"Can not find {filename}. Downloading now...")
    gdf = pygris.counties()
    gdf.to_file(filename, driver='ESRI Shapefile')
    return gdf

# TODO - Improve loop below by testing for name1 >- name2 instead of ==
def generate_borderfile(gdf:gp.GeoDataFrame, filepath:str) -> pd.DataFrame:
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
    match mode:
        case "state":
            url = "https://api.census.gov/data/2019/pep/charagegroups?get=NAME,POP&HISP=0&for=state:*"
        case "county":
            url = "https://api.census.gov/data/2019/pep/charagegroups?get=NAME,POP&HISP=0&for=county:*"
        case _:
            raise ValueError("mode must be 'state' or 'county'")
    session = requests.Session()
    response = session.get(url)
    if response.status_code != 200:
        raise RuntimeError(response.reason)
    data = response.json()
    df = pd.DataFrame(data[1:], columns=data[0])
    df.set_index("NAME", inplace=True)
    df["POP"] = pd.to_numeric(df["POP"])
    df.to_csv(filename)
    return df    

def filter_states_for_contiguous(src_df):
    ret_df = src_df.copy()
    to_keep = [state["name"] for state in CONTIGUOUS_STATES]
    ret_df = ret_df[ret_df.index.isin(to_keep)]
    return ret_df

def filter_counties_for_contiguous(src_df):
    fips_to_keep = [state["state_fp"] for state in CONTIGUOUS_STATES]
    ret_df = src_df.drop(src_df[~src_df["state"].isin(fips_to_keep)].index)
    return ret_df

def main(mode) -> tuple[gp.GeoDataFrame, pd.DataFrame, pd.DataFrame]:
    match mode:
        case "state":
            shape_file = config.STATE_SHAPE_FILENAME
            border_file = config.STATE_BORDERS_FILENAME
            population_file = config.STATE_POPULATIONS_FILENAME
        case "county":
            shape_file = config.COUNTY_SHAPE_FILENAME
            border_file = config.COUNTY_BORDERS_FILENAME
            population_file = config.COUNTY_POPULATIONS_FILENAME
        case _:
            raise ValueError(MODE_ERROR_MESSAGE)
        
    if os.path.exists(shape_file):
        shape_gdf = gp.read_file(shape_file)
    else:
        shape_gdf = download_shapefile(shape_file, mode)
    shape_gdf.set_index("NAME", inplace=True)

    match mode:
        case "state":
            shape_gdf = filter_states_for_contiguous(shape_gdf)
        case "county":
            raise NotImplementedError
            shape_gdf = filter_counties_for_contiguous(shape_gdf)
        case _:
            raise ValueError(MODE_ERROR_MESSAGE)

    if os.path.exists(border_file):
        border_df = utils.df_from_json(border_file, index="name")
    else:
        border_df = generate_borderfile(shape_gdf, border_file)    

    if os.path.exists(population_file):
        population_df = pd.read_csv(population_file, index_col="NAME")
    else:
        population_df = generate_populationfile(population_file, mode)
   
    match mode:
        case "state":
            border_df = filter_states_for_contiguous(border_df)
            population_df = filter_states_for_contiguous(population_df)
        case "county":
            raise NotImplementedError
            border_df = filter_counties_for_contiguous(border_df)
            population_df = filter_states_for_contiguous(population_df)
        case _:
            raise ValueError(MODE_ERROR_MESSAGE)

    return (shape_gdf, border_df, population_df)
        
if __name__ == "__main__":
    main("state")