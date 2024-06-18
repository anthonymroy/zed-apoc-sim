import pandas as pd
from pandera import Check, Column, DataFrameSchema

SimulationSchema = DataFrameSchema(
    {
        'name': Column(str, coerce=True, nullable=False, required=True),
        'population_h': Column(float, coerce=True, nullable=False, required=True),
        'population_z': Column(float, coerce=True, nullable=False, required=True),
        'population_density_h': Column(float, coerce=True, nullable=False, required=True),
        'population_density_z': Column(float, coerce=True, nullable=False, required=True),
        'encounter_chance_h': Column(float, coerce=True, nullable=False, required=True),
        'encounter_chance_z': Column(float, coerce=True, nullable=False, required=True),
        'escape_chance_h': Column(float, coerce=True, nullable=False, required=True),
        'escape_chance_z': Column(float, coerce=True, nullable=False, required=True),
        'bit_h': Column(float, coerce=True, nullable=False, required=True),
        'killed_z': Column(float, coerce=True, nullable=False, required=True),
        'migration_z': Column(float, coerce=True, nullable=False, required=True),
        'border_porosity_z': Column(float, coerce=True, nullable=False, required=True),
        'border_length': Column(float, coerce=True, nullable=False, required=True),
        'area': Column(float, coerce=True, nullable=False, required=True),
        'compactness': Column(float, coerce=True, nullable=False, required=True),
        'neighbors': Column(object, coerce=True, nullable=True, required=True,
                            checks=[Check(lambda x: validate_record(x, NeighborSchema, nullable=True,), element_wise=True)])
    }
)

ShapeSchema = DataFrameSchema(
    {
        'NAME': Column(str, coerce=True, nullable=False, required=True),
        'STATEFP': Column(str, coerce=True, nullable=False, required=True),
        'COUNTYFP': Column(str, coerce=True, nullable=False, required=True),
        'COUNTYNS': Column(str, coerce=True, nullable=False, required=True),
        'GEOID': Column(str, coerce=True, nullable=False, required=True),
        'NAMELSAD': Column(str, coerce=True, nullable=False, required=True),
        'LSAD': Column(str, coerce=True, nullable=False, required=True),
        'CLASSFP': Column(str, coerce=True, nullable=False, required=True),
        'MTFCC': Column(str, coerce=True, nullable=False, required=True),
        'CSAFP': Column(str, coerce=True, nullable=False, required=True),
        'CBSAFP': Column(str, coerce=True, nullable=False, required=True),
        'METDIVFP': Column(str, coerce=True, nullable=False, required=True),
        'FUNCSTAT': Column(str, coerce=True, nullable=False, required=True),
        'ALAND': Column(float, coerce=True, nullable=False, required=True),
        'AWATER': Column(float, coerce=True, nullable=False, required=True),
        'INTPTLAT': Column(str, coerce=True, nullable=False, required=True),
        'INTPTLON': Column(str, coerce=True, nullable=False, required=True),
        'geometry': Column(object, coerce=True, nullable=False, required=True)
    }
)

NeighborSchema = DataFrameSchema(
    {
        'name': Column(str, coerce=True, nullable=False, required=True),
        'shared_border_length': Column(float, coerce=True, nullable=False, required=True),
        'fraction': Column(float, coerce=True, nullable=True, required=True)
    }
)

GraphSchema = DataFrameSchema(
    {
        'name': Column(str, coerce=True, nullable=False, required=True),
        'border_length': Column(float, coerce=True, nullable=False, required=True),
        'neighbors': Column(object, coerce=True, nullable=True, required=True,
                            checks=[Check(lambda x: validate_record(x, NeighborSchema, nullable=True,), element_wise=True)])
    }
)

PopulationSchema = DataFrameSchema(
    {
        'NAME': Column(str, coerce=True, nullable=False, required=True),
        'POP': Column(float, coerce=True, nullable=False, required=True),
        'HISP': Column(str, coerce=True, nullable=False, required=True),
        'state': Column(str, coerce=True, nullable=False, required=True),
        'county': Column(str, coerce=True, nullable=False, required=False)
    }
)

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