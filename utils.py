import json
import math
from matplotlib.colors import ListedColormap
import numpy as np
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

def sigmoid2(x:float) -> float:
    return 1 / (1 + math.exp(-x))

def safe_log10(x:float) -> float:
    if x < 1 :
        return 0
    return math.log10(x)

def calculate_key_frames_linear(data_length:int, number_of_frames:int) -> list[int]:
    '''
    Gets a linear distribution of the desired number_of_frames between [0, data_length]
    '''
    frame_step_size = float(data_length) / number_of_frames
    key_frames = []
    for i in range(number_of_frames):
        key_frames.append(round(i*frame_step_size))
    return key_frames

def calculate_key_frames_logarithmic(data_length:int, number_of_frames:int) -> list[int]:
    '''
    Gets a logarithmic distribution of the desired number_of_frames between [0, data_length]
    '''    
    key_frames = [0]
    frame_step_size = math.pow(data_length, 1/number_of_frames)
    for i in range(number_of_frames):
        key_frames.append(round(math.pow(frame_step_size, i)))
    key_frames.append(data_length-1)
    return key_frames

def interpolate_rgb(x, arr0, arr1):
    ret = []
    for i in range(len(arr0)):
        y = arr0[i] + x * (arr1[i] - arr0[i])
        ret.append(y)
    return ret

if __name__ == "__main__":
    # For development and testing
    pass