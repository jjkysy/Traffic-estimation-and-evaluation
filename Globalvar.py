# -*- coding: utf-8 -*-
"""
Created on Fri Aug  3 11:27:03 2018

@author: yao
"""
import numpy as np
import pdb
import traci
# simulation
on_ramp_lag = 500
p_rate_ramp = 0.5
p_rate_main = 0.5
demand_main_free = 500
demand_main_peak = 1200
demand_ramp = (300, 900)
demand_time = 10800
peak_time = [(1000, 1600), (5900, 6500)]
road_length = [5000, 250, 2500]
rl = np.asarray(road_length, dtype=int)
total_length = rl.sum()
det_l1_location = np.arange(0, road_length[0], 100, dtype=int)
det_l2_location = np.arange(5000, road_length[1]+5000, 100, dtype=int)
det_l3_location = np.arange(5250, road_length[2]+1+5250, 100, dtype=int)
# pdb.set_trace()
det_location = {'l1': det_l1_location, 'l2': det_l2_location, 'l3': det_l3_location}
optnr = 4  # optimal platoon size
ramp_metering = 0 # ramp metering switch
asm = 0 # asm switch
speed_limit = 23
step_length = 0.1
cr_occupancy = 16

