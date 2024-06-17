import config
import geopandas as gpd
import numpy as np
import pandas as pd

def set_features(index:list) -> pd.DataFrame:
    df = pd.DataFrame(columns=[
        "population_h",
        "population_z",
        "population_density_h",
        "population_density_z",
        "encounter_chance_h",
        "encounter_chance_z",
        "escape_chance_h",
        "escape_chance_z",
        "bit_h",
        "killed_z",
        "migration_z",
        "border_porosity_z",
        "border_length",
        "area",
        "compactness",
        "neighbors"
    ])
    df["index"] = index
    df.set_index("index", inplace=True)
    return df

def set_initial_conditions(src_df:pd.DataFrame, p_df:pd.DataFrame) -> pd.DataFrame:
     ret_df = src_df.copy()
     ret_df["population_h"] = p_df["POP"]
     ret_df["escape_chance_h"] = config.INITIAL_ESCAPE_CHANCE_H
     ret_df["escape_chance_z"] = config.INITIAL_ESCAPE_CHANGE_Z
     ret_df["border_porosity_z"] = config.BORDER_POROSITY
     ret_df.fillna(0.0, inplace=True)
     #ZOMBIE ATTACK!     
     ret_df.at["Pennsylvania", "population_z"] = round(0.01*ret_df.at["Pennsylvania", "population_h"])
     return ret_df

def calculate_static_values(src_df:pd.DataFrame, gdf:gpd.GeoDataFrame, b_df:pd.DataFrame) -> pd.DataFrame:
    ret_df = src_df.copy()
    ret_df["border_length"] = b_df["border_length"]
    ret_df["area"] = gdf.area 
    ret_df["compactness"] = gdf.area / gdf.geometry.convex_hull.area 
    ret_df["neighbors"] = b_df["neighbors"] 
    return ret_df

def calculate_migration(src_df:pd.DataFrame) -> pd.Series:
    ret_df = src_df.copy()
    ret_df["migration"] = 0
    for my_name in ret_df.index:
        total = 0
        my_conc = ret_df.at[my_name,"population_density_z"]
        my_area = ret_df.at[my_name,"area"]
        my_porosity = ret_df.at[my_name,"border_porosity_z"]
        my_compactness = ret_df.at[my_name,"compactness"]
        for neighbor in ret_df.at[my_name,"neighbors"]:
            name_n = neighbor["name"]
            conc_n = ret_df.at[name_n,"population_density_z"]
            fraction = neighbor["fraction"]
            rate_n = my_porosity * fraction / my_compactness
            total += rate_n * (conc_n - my_conc) * my_area
        ret_df.at[my_name,"migration"] = int(total)
    return ret_df["migration"]

def calculate_derived_values(src_df:pd.DataFrame) -> pd.DataFrame:    
    ret_df = src_df.copy()
    ret_df["population_density_h"] = ret_df["population_h"] / ret_df["area"]
    ret_df["population_density_z"] = ret_df["population_z"] / ret_df["area"]
    ret_df["encounter_chance_h"] = ret_df["population_z"] / (ret_df["population_h"] + ret_df["population_z"])
    ret_df["encounter_chance_z"] = ret_df["population_h"] / (ret_df["population_h"] + ret_df["population_z"])
    ret_df["bit_h"] = (ret_df["population_h"] * ret_df["encounter_chance_h"] * (1 - ret_df["escape_chance_h"])).apply(np.ceil)
    ret_df["bit_h"] = ret_df["bit_h"].apply(max, args=(0,))
    ret_df["killed_z"] = (ret_df["population_z"] * ret_df["encounter_chance_z"] * (1 - ret_df["escape_chance_z"])).apply(np.ceil)
    ret_df["killed_z"] = ret_df["killed_z"].apply(max, args=(0,))
    ret_df["migration_z"] = (calculate_migration(ret_df) * ret_df["encounter_chance_z"] * (1 - ret_df["escape_chance_z"])).apply(np.round)
    return ret_df

def initialize(shape_gdf:gpd.GeoDataFrame, border_df:pd.DataFrame, population_df:pd.DataFrame) -> pd.DataFrame:
    ret_df = set_features(list(shape_gdf.index))
    ret_df = calculate_static_values(ret_df, shape_gdf, border_df)
    ret_df = set_initial_conditions(ret_df, population_df)
    ret_df = calculate_derived_values(ret_df)
    return ret_df        

def time_step(src_df:pd.DataFrame) -> pd.DataFrame:
    ret_df = src_df.copy()
    ret_df["population_h"] = ret_df["population_h"] - ret_df["bit_h"]
    ret_df["population_h"] = ret_df["population_h"].apply(max, args=(0,))
    ret_df["population_z"] = ret_df["population_z"] + ret_df["bit_h"] - ret_df["killed_z"] + ret_df["migration_z"]
    ret_df["population_z"] = ret_df["population_z"].apply(max, args=(0,))
    ret_df = calculate_derived_values(ret_df)
    return ret_df

def run(initial_df:pd.DataFrame) -> list[pd.DataFrame]:
    df_0 = initial_df.copy()
    data = [df_0]
    for i in range(config.DAYS_TO_SIMULATE): 
        if i % 50 == 0:
            print(f"Day {i} of simulation.")       
        df_1 = time_step(df_0)
        df_0 = df_1.copy()
        data.append(df_0)
    return data

if __name__ == "__main__":
    import setup
    shape_gdf, border_df, population_df = setup.main("state")
    initial_df = initialize(shape_gdf, border_df, population_df)