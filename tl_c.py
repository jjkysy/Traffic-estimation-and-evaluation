# -*- coding: utf-8 -*-
"""
Created on Fri Oct  5 11:10:29 2018

@author: yao
"""
from __future__ import absolute_import
from __future__ import print_function
import math
import traci
import re
import Globalvar
import pdb


class TrafficLight:
    def __init__(self, tl_id, simstep):
        self.id = tl_id
        self.simstep = simstep
        self.siml = Globalvar.step_length
        self.det_id = "l2_13"
        self.c_inter = 60 # decision interval
        self.cycle = 54.0 # fixed cycle time
        self.t_max = 44.0 # max phase
        self.t_min = 10.0 # min phase

    def vehicle_count(self, occupancy):
        # count occupancy for the last 60 second
        if traci.inductionloop.getVehicleData(self.det_id):
            v_data = traci.inductionloop.getVehicleData(self.det_id)
            if v_data[0][3] != -1:
                # pdb.set_trace()
                occupancy += v_data[0][3]-v_data[0][2]
        return occupancy

    def alinea(self, occupancy):
        phase = []
        occupancy = self.vehicle_count(occupancy)
        kr = 70 # hyper parameter for alinea
        if self.simstep * self.siml % self.c_inter == 0 and self.simstep != 0:
            # pdb.set_trace()
            occupancy = (occupancy/self.c_inter)*100
            green_last = self.cycle-traci.trafficlight.getPhaseDuration('2') # last interval green time
            r_last = 0.33*green_last-1.45 # transfer to saturation flow
            r_next = r_last + kr * ((Globalvar.cr_occupancy - occupancy)/100) # alinea, feedback control
            green_next = round((r_next+1.45)/0.33) # transfer to green time
            green = float(max(min(green_next, self.t_max), self.t_min)) # fit in limitation
            red = self.cycle - green
            phase.append(traci.trafficlight.Phase(red, "rG", red, red))
            phase.append(traci.trafficlight.Phase(3, "yG", 0, 0))
            phase.append(traci.trafficlight.Phase(green, "GG", green, green))
            phase.append(traci.trafficlight.Phase(3, "yG", 0, 0))
            logic = traci.trafficlight.Logic("p-alinea", 0, 0, phase)
            traci.trafficlight.setCompleteRedYellowGreenDefinition(self.id, logic)
            # set new signal logic for the next cycle
            occupancy = 0 # reset
        return occupancy