import ast
import pandas as pd
from pandera import Check, Column, DataFrameSchema, Index

SimulationSchema = DataFrameSchema({
    "name": Column(str, coerce=True, nullable=False, required=False,
                            description="Name of the region"),
    "population_h": Column(int, coerce=True, nullable=False, required=True,
                            description="Number of people in the region"),
    "population_z": Column(int, coerce=True, nullable=False, required=True,
                            description="Number of zeds in the region"),
    "population_d": Column(int, coerce=True, nullable=False, required=True,
                            description="Number of zeds in the region"),
    "encounters": Column(float, coerce=True, nullable=False, required=True,
                                    description="Number of encounters"),                              
    "escape_chance_h": Column(float, coerce=True, nullable=False, required=True, 
                                description="Probability of a person escaping an encounter uninfected"),
    "escape_chance_z": Column(float, coerce=True, nullable=False, required=True,
                                description="Probability of a zed escaping an encounter undead"),
    "cumulative_encounters_h": Column(float, coerce=True, nullable=False, required=True,
                                        description="Average number of encouters a person has had"),
    "bit_h": Column(int, coerce=True, nullable=False, required=True,
                    description="Number of people infected"),
    "killed_z": Column(int, coerce=True, nullable=False, required=True,
                        description="Number of zeds killed"),
    "migration_z": Column(int, coerce=True, nullable=False, required=True,
                            description="Number of zeds that have moved across regions"),
    "border_length": Column(float, coerce=True, nullable=False, required=True,
                            description="Perimeter of region (km)"),
    "area": Column(float, coerce=True, nullable=False, required=True,
                    description="Land area of region (km^2)"),
    "border_area_z": Column(float, coerce=True, nullable=False, required=True,
                            description="Area close enough to border for zed migration (km^2)"),
    "neighbors": Column(object, coerce=True, nullable=True, required=True,
                        checks=[Check(lambda x: validate_record(x, NeighborSchema, nullable=True,), element_wise=True)],
                        description="List of neighboring regions")
})

ShapeSchema = DataFrameSchema({            
    "STATEFP": Column(str, coerce=True, nullable=False, required=True),
    "COUNTYFP": Column(str, coerce=True, nullable=False, required=False),
    "NAME": Column(str, coerce=True, nullable=False, required=True),
    "ALAND": Column(float, coerce=True, nullable=False, required=True),
    "AWATER": Column(float, coerce=True, nullable=False, required=True),
    "geometry": Column("geometry", coerce=True, nullable=False, required=True)    
})

NeighborSchema = DataFrameSchema({        
    "neighbor_id": Column(str, coerce=True, nullable=False, required=True),
    "neighbor_state_fp": Column(str, coerce=True, nullable=False, required=True),
    "neighbor_county_fp": Column(str, coerce=True, nullable=False, required=False),
    "neighbor_name": Column(str, coerce=True, nullable=False, required=True),
    "shared_border_length": Column(float, coerce=True, nullable=False, required=True)
})

GraphSchema = DataFrameSchema({
    "state_fp": Column(str, coerce=True, nullable=False, required=True),
    "county_fp": Column(str, coerce=True, nullable=False, required=False),
    "name": Column(str, coerce=True, nullable=False, required=True),
    "border_length": Column(float, coerce=True, nullable=False, required=True),
    "neighbors": Column(object, coerce=True, nullable=True, required=True,
                        checks=[Check(lambda x: validate_record(x, NeighborSchema, nullable=True,), element_wise=True)])
})

PopulationSchema = DataFrameSchema( {
    "POP": Column(int, coerce=True, nullable=False, required=True),
    "HISP": Column(int, coerce=True, nullable=False, required=True),
    "state": Column(str, coerce=True, nullable=False, required=True),
    "county": Column(str, coerce=True, nullable=False, required=True)
})

def validate_record(record_list:list, record_schema:DataFrameSchema, nullable:bool = False) -> bool:
    records = pd.Series(record_list)
    try:
        if len(records) == 0 or all(pd.isnull(records)):
            return nullable
        if nullable:
            records = records.dropna()
        df = pd.DataFrame.from_records(records)
        record_schema.validate(df)
        return True
    except:
        return False

def safe_literal_eval(text:str) -> any:
    try:
        return ast.literal_eval(text)
    except:
        return text
        
def clean_df(df:pd.DataFrame, schema:DataFrameSchema) -> pd.DataFrame:
    #Remove empty colums and rows
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
    df.dropna(axis="index", how="all", inplace=True)
    #Convert strings to the lists and/or boolean they are supposed to represent
    for key in schema.columns:
        if key not in df.columns:
            continue
        df[key] = df[key].apply(safe_literal_eval)
    #Wierd things happen when trying to set a type of an empty column, so we drop them
    df.dropna(axis="columns", how="all", inplace=True)
    df = schema(df, lazy=True)    
    return df