# Pacakge Imports
from utils import *
import importlib
import utils
importlib.reload(utils)
import os.path
from os import path
import matplotlib.pyplot as plt
import math
import pandas as pd

class Visualization : 
    def __init__(self, pole_num, camera_num) :
        """ Constructor. Creates a path to the correct CSV file for visualization functions to use. """
        
        data_path = pathlib.Path().absolute().joinpath('../csvData')
        self.file_name = data_path.joinpath(f'p{pole_num}c{camera_num}.csv')
        self.pole_num = pole_num
        self.camera_num = camera_num
        
    def time_space_graph(self, car_lane, start_frame, end_frame) :
        """ Creates a Time vs. Space graph for the cars in a single lane.
    
        Args :
            car_lane : Desired lane number to analyze.
            start_frame : Starting frame number for the plot.
            end_frame : Ending frame number for the plot.
        """
        
        camera_min, camera_max = find_camera_range(self.camera_num)
        
        df = read_data(self.file_name, 0)
        df = query_df(df, car_lane, start_frame, end_frame)
        id_arr = df.ID.unique()
        
        fig, ax = plt.subplots(figsize=(7,7))
        ax.set_aspect('auto')
        plt.xlim(start_frame, end_frame)
        plt.ylim(camera_min, camera_max)
        
        for car_id in id_arr : 
            car_snap = df.loc[df['ID'] == car_id]
            car_snap = car_snap.sort_values(by=['Frame #']).reset_index()
            
            x_ar = get_frame(car_snap)
            front_y = get_position(car_snap, 'fbr_x')
            back_y = get_position(car_snap, 'bbr_x')
            rgb = (random.random(), random.random(), random.random())
            
            plt.plot(x_ar, front_y, color=rgb)
            plt.plot(x_ar, back_y, color=rgb)
            plt.fill_between(x_ar, front_y, back_y, color=rgb, label=f'Car #{car_id}')

        plt.title(f'Camera #{self.camera_num}, Lane #{car_lane}', fontdict={'fontsize':'x-large'}, pad=20)
        plt.xlabel('Frame #')
        plt.ylabel('Car Positions( ft )')
        plt.legend(loc='upper center', bbox_to_anchor=(1.15, 1), fancybox=True, shadow=True, ncol=1)
        plt.savefig(f'../Output Graphs/p{self.pole_num}c{self.camera_num}_lane{car_lane}_timespace.jpg',  bbox_inches='tight')

    def time_speed_graph(self, car_lane, start_frame, end_frame) :
        x_ar, speed_ar = [], []
        df = read_data(self.file_name, 0)
        df = query_df(df, car_lane, start_frame, end_frame)
        
        fig, ax = plt.subplots(figsize=(7,7))
        ax.set_aspect('auto')
        plt.xlim(start_frame, end_frame)
        plt.ylim(30, 40)
        
        for i in range(start_frame, end_frame) :
            frame_snap = df.loc[df['Frame #'] == i].reset_index()
            
            x_ar.append(i)
            speed_ar.append(compute_avg_speed(frame_snap))
            
        plt.plot(x_ar, speed_ar, color='darkcyan')
        plt.title(f'Camera #{self.camera_num}, Lane #{car_lane}\nAverage Speed vs. Frame', fontdict={'fontsize':'x-large'}, pad=20)
        plt.xlabel('Frame #')
        plt.ylabel('Avg Speed (m/s)')
        plt.savefig(f'../Output Graphs/p{self.pole_num}c{self.camera_num}_lane{car_lane}_timespeed.jpg',  bbox_inches='tight')
        
        
# Free Functions
def read_data(file_name, skiprows = 0, index_col = False) :
    """ Transforms a csv file into a Pandas DataFrame.
    The only factors we are concerned about in plotting is the front_x position, back_x position,
    y postition, Frame#, Timestamp, and ID.
    
    Args :
        file_name : The location / name of the Matrix CSV file.
        
    Return :
        The queryed DataFrame.
    """
    
    df = pd.read_csv(file_name, skiprows = skiprows,error_bad_lines=False,index_col = index_col)
    df = df[['fbr_x','bbr_x','y','Frame #','Timestamp','ID','speed']]
    df = df.fillna(0.0)

    return df


def find_camera_range(camera_num) :    
    """ Helper function that acts like a dictionary to find the visual range 
    of the camera from the inputted camera_num. 
    
    Args :
        camera_num : The number of the Camera that we want to find the range for.
        
    Return :
        2 ints : first is the starting point of the Camera's vision, second is the end.
    """
    # Originally, 3 : [630, 790]. Changed for some plot testing.
    # Originally, 4 : [640, 810]
    
    cam_range = {
        1 : [200, 440],
        2 : [400, 680],
        3 : [630, 790],
        4 : [600, 810],
        5 : [700, 950],
        6 : [820, 1240],
        'all': [200, 1200]
    }

    return cam_range[camera_num][0], cam_range[camera_num][1]


def query_df(df, car_lane, start_frame, end_frame) :
    """ Querys the DataFrame with only the lanes and frame range that we want.
    
    Args :
        df : DataFrame will full info from CSV file.
        lane_to_check : Desired lane number to analyze.
        start_frame : Starting frame number for the plot.
        end_frame : Ending frame number for the plot.
        
    Return :
        The queryed DataFrame.
    """
    
    y_range = {
        1 : [0, 12],
        2 : [12, 24],
        3 : [24, 36],
        4 : [36, 48],
        5 : [72, 84],
        6 : [84, 96],
        7 : [96, 108],
        8 : [108, 120]
    }
    y_min, y_max = y_range[car_lane][0], y_range[car_lane][1]

    df = df.loc[df['y'] >= (y_min / 3.28084)]
    df = df.loc[df['y'] <= (y_max / 3.28084)]
    df = df.loc[df['Frame #'] >= start_frame]
    df = df.loc[df['Frame #'] <= end_frame]

    return df;


def get_frame(car_df) :
    frame_x = []

    for i in range(len(car_df)) :
        frame_x.append(car_df.at[i, 'Frame #'])

    return frame_x


def get_position(car_df, msg) :
    position_y = []
    
    for i in range(len(car_df)) :
        position_y.append(car_df.at[i, msg] * 3.28084)
        
    return position_y


def compute_avg_speed(df) :
    avg = 0.0
    
    for i in range(len(df)) :
        avg += df.at[i, 'speed']
        
    if len(df) == 0 :
        return 0.0
    
    return avg / (len(df))