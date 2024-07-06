from config import Settings
import data.schema as sch
import geopandas as gpd
import numpy as np
import pandas as pd
import random 
import utils

def outbreak(src_df:pd.DataFrame, ground_zero:str) -> pd.DataFrame:
    ret_df = src_df.copy()
    if ground_zero not in list(ret_df.index):
        ground_zero = random.choice(list(ret_df.index))   
    #ret_df.at[ground_zero, "population_z"] = 0.001*ret_df.at[ground_zero, "population_h"]   
    ret_df.at[ground_zero, "population_z"] = 1
    return ret_df

def set_features(index:list) -> pd.DataFrame:
    df = pd.DataFrame(columns=sch.SimulationSchema.columns)
    df["index"] = index
    df.set_index("index", inplace=True)    
    return df

def set_initial_conditions(src_df:pd.DataFrame, p_df:pd.DataFrame, ground_zero:str) -> pd.DataFrame:
    ret_df = src_df.copy()
    ret_df["population_h"] = p_df["POP"]  
    # Calling infer_objects prevents downcasting FutureWarning
    ret_df = ret_df.infer_objects(copy=False).fillna(0.0)
    ret_df = outbreak(ret_df, ground_zero)
    return ret_df

def calculate_static_values(
        src_df:pd.DataFrame,
        gdf:gpd.GeoDataFrame,
        b_df:pd.DataFrame,
        distance_z:float
    ) -> pd.DataFrame:
    
    ret_df = src_df.copy()
    ret_df["border_length"] = b_df["border_length"]
    ret_df["area"] = gdf["ALAND"] * 1e-6 #km^2
    ret_df["border_area_z"] = (ret_df["border_length"]*distance_z).clip(upper= ret_df["area"])
    ret_df["neighbors"] = b_df["neighbors"] 
    return ret_df

def calculate_migration(src_df:pd.DataFrame) -> pd.Series:
    ret = pd.Series(index=src_df.index)
    for my_name in ret.index:
        total = 0        
        my_conc = (src_df.at[my_name,"population_z"] - src_df.at[my_name,"killed_z"]) / src_df.at[my_name,"area"]        
        for neighbor in src_df.at[my_name,"neighbors"]:
            neighbor_name = neighbor["neighbor_name"]
            neighbor_conc = (src_df.at[neighbor_name,"population_z"] - src_df.at[neighbor_name,"killed_z"]) / src_df.at[neighbor_name,"area"]
            neighbor_border_zeds = my_conc * src_df.at[neighbor_name,"border_area_z"]            
            shared_border_length = neighbor["shared_border_length"]
            my_fraction = shared_border_length / src_df.at[my_name,"border_length"]
            neighbor_fraction = shared_border_length / src_df.at[neighbor_name,"border_length"]
            my_border_zeds = my_conc * my_fraction * src_df.at[my_name,"border_area_z"]
            neighbor_border_zeds = neighbor_conc * neighbor_fraction * src_df.at[neighbor_name,"border_area_z"]
            base_migration = (neighbor_border_zeds - my_border_zeds) / 2 
            if base_migration != 0:
                rate = abs(neighbor_conc - my_conc)/(neighbor_conc + my_conc)
                total += int(rate*base_migration)
        ret[my_name] = total    
    if(sum(ret) != 0):
        raise RuntimeError("Round-off error. Migration sum does not equal zero")
    return ret

def calculate_escape_chance(cumulative_encounters, initial, final, m, b):
    scale = final - initial
    ret = utils.sigmoid(cumulative_encounters, m, b)
    ret = initial + scale*ret
    return ret
    
def calculate_derived_values(src_df:pd.DataFrame, settings:Settings) -> pd.DataFrame:    
    ret_df = src_df.copy()
    ret_df["population_density_h"] = ret_df["population_h"] / ret_df["area"]
    ret_df["population_density_z"] = ret_df["population_z"] / ret_df["area"]
    speed_z = settings.zed_speed * 1.609 * 24 #Convert from mph to km/day
    area_z = speed_z * 1 * settings.encounter_distance * 3.048e-4 #km^2
    ret_df["encounters"] = ret_df["population_density_h"] * area_z * ret_df["population_z"]
    ret_df["escape_chance_h"] = ret_df["cumulative_encounters_h"].apply(
        calculate_escape_chance, args=(
            settings.initial_escape_chance_h,
            settings.final_escape_chance_h,
            settings.escape_learning_rate_h,
            settings.escape_learning_threshold_h
        )
    )
    ret_df["escape_chance_z"] = ret_df["cumulative_encounters_h"].apply(
        calculate_escape_chance, args=(
            settings.initial_escape_chance_z,
            settings.final_escape_chance_z,
            settings.combat_learning_rate_h,
            settings.combat_learning_threshold_h
        )
    )
    ret_df["bit_h"] = (ret_df["encounters"] * (1 - ret_df["escape_chance_h"])).apply(np.round)   
    ret_df["bit_h"] = ret_df["bit_h"].clip(lower=0, upper=ret_df["population_h"])
    ret_df["killed_z"] = (ret_df["encounters"] * (1 - ret_df["escape_chance_z"])).apply(np.round)
    ret_df["killed_z"] = ret_df["killed_z"].clip(lower=0, upper=ret_df["population_z"])
    ret_df["migration_z"] = calculate_migration(ret_df).apply(np.round)    
    return ret_df

def initialize(
        shape_gdf:gpd.GeoDataFrame,
        border_df:pd.DataFrame,
        population_df:pd.DataFrame,
        settings:Settings
    ) -> pd.DataFrame:

    ret_df = set_features(list(shape_gdf.index))
    zed_travel_distance = settings.zed_speed*1.609*24*1 #Convert from mph to km in 1 day
    ret_df = calculate_static_values(ret_df, shape_gdf, border_df, zed_travel_distance)    
    ret_df = set_initial_conditions(ret_df, population_df, settings.outbreak_region)
    ret_df = sch.clean_df(ret_df, sch.SimulationSchema)
    ret_df = calculate_derived_values(ret_df, settings)
    return ret_df        

def time_step(src_df:pd.DataFrame, settings:Settings) -> pd.DataFrame:
    ret_df = src_df.copy()
    ret_df["population_h"] = ret_df["population_h"] - ret_df["bit_h"]
    ret_df["population_h"] = ret_df["population_h"].apply(max, args=(0,))
    ret_df["population_z"] = ret_df["population_z"] + ret_df["bit_h"] - ret_df["killed_z"] + ret_df["migration_z"]
    ret_df["population_z"] = ret_df["population_z"].apply(max, args=(0,)) 
    ret_df["population_d"] = ret_df["population_d"] + ret_df["killed_z"]
    populated_mask = ret_df[ret_df["population_h"] > 0]
    ret_df.loc[populated_mask.index,"cumulative_encounters_h"] += \
        ret_df.loc[populated_mask.index,"encounters"] / ret_df.loc[populated_mask.index,"population_h"]
    ret_df = calculate_derived_values(ret_df, settings)
    return ret_df

def run(initial_df:pd.DataFrame, settings:Settings) -> list[pd.DataFrame]:
    intial_population = sum(initial_df["population_h"]) + sum(initial_df["population_z"]) + sum(initial_df["population_d"])
    df_0 = initial_df.copy()
    data = [df_0]
    for i in range(settings.simulation_length): 
        if i % 50 == 0:
            print(f"Day {i} of simulation.")       
        df_1 = time_step(df_0, settings)
        total_population = sum(df_1["population_h"]) + sum(df_1["population_z"]) + sum(df_1["population_d"])
        if total_population != intial_population:
            raise RuntimeError("Population has changed")
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
    from config import Filepaths
    my_settings = Settings()
    my_filepaths = Filepaths()
    shape_gdf, border_df, population_df = setup.main(my_settings, my_filepaths)
    initial_df = initialize(shape_gdf, border_df, population_df, my_settings)
    print(initial_df.loc[initial_df.index[0]])