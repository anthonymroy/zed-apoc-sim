import config
import data.schema as sch
import geopandas as gpd
import numpy as np
import pandas as pd
import random 
import utils

def outbreak(src_df:pd.DataFrame) -> pd.DataFrame:
    ret_df = src_df.copy()
    ground_zero = config.OUTBREAK_START
    if ground_zero not in list(ret_df.index):
        ground_zero = random.choice(list(ret_df.index))      
    ret_df.at[ground_zero, "population_z"] = 1
    return ret_df

def set_features(index:list) -> pd.DataFrame:
    df = pd.DataFrame(columns=sch.SimulationSchema.columns)
    df["index"] = index
    df.set_index("index", inplace=True)    
    return df

def set_initial_conditions(src_df:pd.DataFrame, p_df:pd.DataFrame) -> pd.DataFrame:
    ret_df = src_df.copy()
    ret_df["population_h"] = p_df["POP"]  
    ret_df = ret_df.fillna(0.0)
    ret_df = outbreak(ret_df)
    return ret_df

def calculate_static_values(src_df:pd.DataFrame, gdf:gpd.GeoDataFrame, b_df:pd.DataFrame) -> pd.DataFrame:
    ret_df = src_df.copy()
    ret_df["speed_z"] = config.ZED_SPEED * 1.609 * 24 #Convert from mph to km/day
    ret_df["border_length"] = b_df["border_length"]
    ret_df["border_porosity_z"] = config.BORDER_POROSITY
    ret_df["area"] = gdf["ALAND"] * 1e-6 #km^2 
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
            name_n = neighbor["neighbor_name"]
            conc_n = ret_df.at[name_n,"population_density_z"]
            fraction = neighbor["fraction"]
            rate_n = my_porosity * fraction / my_compactness
            total += int(rate_n * (conc_n - my_conc) * my_area)
        ret_df.at[my_name,"migration"] = int(total)
    ret_df["migration"].clip(lower= -1*ret_df["population_z"])
    return ret_df["migration"]

def calculate_escape_chance(cumulative_encounters, initial, final, m, b):
    scale = final - initial
    #ret = cumulative_encounters.apply(utils.sigmoid, args=(m, b))
    ret = utils.sigmoid(cumulative_encounters, m, b)
    ret = initial + scale*ret
    return ret
    
def calculate_derived_values(src_df:pd.DataFrame) -> pd.DataFrame:    
    ret_df = src_df.copy()
    learning_asymptote = 0.99 
    ret_df["population_density_h"] = ret_df["population_h"] / ret_df["area"]
    ret_df["population_density_z"] = ret_df["population_z"] / ret_df["area"]
    speed_z = config.ZED_SPEED * 1.609 * 24 #Convert from mph to km/day
    area_z = speed_z * 1 * config.ENCOUNTER_DISTANCE * 3.048e-4 #km^2
    ret_df["encounters"] = ret_df["population_density_h"] * area_z * ret_df["population_z"]
    #ret_df["escape_chance_h"] = learning_asymptote*ret_df["cumulative_encounters_h"].apply(utils.sigmoid, args=(1.1, 2))
    #ret_df["escape_chance_z"] = 1 - learning_asymptote*ret_df["cumulative_encounters_h"].apply(utils.sigmoid, args=(1, 4))
    ret_df["escape_chance_h"] = ret_df["cumulative_encounters_h"].apply(
        calculate_escape_chance, args=(config.INITIAL_ESCAPE_CHANCE_H, config.FINAL_ESCAPE_CHANCE_H, 1, 1))
    ret_df["escape_chance_z"] = ret_df["cumulative_encounters_h"].apply(
        calculate_escape_chance, args=(config.INITIAL_ESCAPE_CHANCE_Z, config.FINAL_ESCAPE_CHANCE_Z, 1, 2))
    ret_df["bit_h"] = (ret_df["encounters"] * (1 - ret_df["escape_chance_h"])).apply(np.round)   
    ret_df["bit_h"] = ret_df["bit_h"].clip(lower=0, upper=ret_df["population_h"])
    ret_df["killed_z"] = (ret_df["encounters"] * (1 - ret_df["escape_chance_z"])).apply(np.round)
    ret_df["killed_z"] = ret_df["killed_z"].clip(lower=0, upper=ret_df["population_z"])
    ret_df["migration_z"] = calculate_migration(ret_df).apply(np.round)
    return ret_df

def initialize(shape_gdf:gpd.GeoDataFrame, border_df:pd.DataFrame, population_df:pd.DataFrame) -> pd.DataFrame:
    ret_df = set_features(list(shape_gdf.index))
    ret_df = calculate_static_values(ret_df, shape_gdf, border_df)    
    ret_df = set_initial_conditions(ret_df, population_df)
    ret_df = sch.clean_df(ret_df, sch.SimulationSchema)
    ret_df = calculate_derived_values(ret_df)
    return ret_df        

def time_step(src_df:pd.DataFrame) -> pd.DataFrame:
    ret_df = src_df.copy()
    ret_df["population_h"] = ret_df["population_h"] - ret_df["bit_h"]
    ret_df["population_h"] = ret_df["population_h"].apply(max, args=(0,))
    ret_df["population_z"] = ret_df["population_z"] + ret_df["bit_h"] - ret_df["killed_z"] + ret_df["migration_z"]
    ret_df["population_z"] = ret_df["population_z"].apply(max, args=(0,)) 
    populated_mask = ret_df[ret_df["population_h"] > 0]
    ret_df.loc[populated_mask.index,"cumulative_encounters_h"] += \
        ret_df.loc[populated_mask.index,"encounters"] / ret_df.loc[populated_mask.index,"population_h"]
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

def summarize(simulation:list[pd.DataFrame]) -> pd.DataFrame:
    summary = []
    for day in range(len(simulation)):
        total_h = sum(simulation[day]['population_h'])
        total_z = sum(simulation[day]['population_z'])
        summary.append({
            "day": day,
            "population_h_log10": utils.safe_log10(total_h),
            "population_z_log10": utils.safe_log10(total_z)
        })
    return pd.DataFrame.from_records(summary, index="day")

if __name__ == "__main__":
    import setup
    region = "IN"
    shape_gdf, border_df, population_df = setup.main(region)
    initial_df = initialize(shape_gdf, border_df, population_df)
    print(initial_df.loc[initial_df.index[0]])