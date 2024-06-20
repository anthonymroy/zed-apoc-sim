import json
import math
from pandas import DataFrame
import shapely.geometry as sg

def get_border_length(polygon:sg.Polygon) -> float:
    return polygon.length

def get_shared_border_length(polygon1:sg.Polygon, polygon2:sg.Polygon) -> float:
    border = polygon1.intersection(polygon2)
    return border.length

def write_json_file(json_object:list[dict], filename:str) -> None:
    json_object = json.dumps(json_object, indent=4)
    with open(filename, "w") as f:
        f.write(json_object)

def read_json_file(filename:str) -> list[dict]:    
    with open(filename, "r") as f:
        json_object = json.load(f)
    return json_object

def df_from_json(filename:str, index=None) -> DataFrame:
    data = read_json_file(filename)
    return DataFrame.from_records(data, index=index)

def sigmoid(x:float, m:float=1, b:float=0) -> float:
    return 1 / (1 + math.exp(-m*(x-b/m)))

def safe_log(x:float) -> float:
    if x <= 0:
        return 0
    return math.log10(x)

if __name__ == "__main__":
    # For development and testing
    pass