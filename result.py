# -*- coding: utf-8 -*-
"""
Created on Tue Jul 17 16:48:54 2018

@author: yao

attention: matrix v has 1 step latency, due to traci.getSpeed trace back the 
last timestep speed
"""

from __future__ import absolute_import
from __future__ import print_function

import pdb
import matplotlib.pyplot as plt
import numpy as np
import Globalvar
import xml.dom.minidom as xmld
import math


# import math

def get_attrvalue(node, attrname):
    return node.getAttribute(attrname) if node else ''


def get_nodevalue(node, index=0):
    return node.childNodes[index].nodeValue if node else ''


def get_xmlnode(node, name):
    return node.getElementsByTagName(name) if node else []


class Result:

    def __init__(self, av_list, simstep):
        self.av = av_list  # loaded vehicles av list
        self.step = simstep
        self.total_time = self.step
        self.total_length = Globalvar.total_length
        self.speed_contour_matrix = -np.ones([self.total_length + 1, self.total_time + 1])
        self.ms_demand = Globalvar.demand_main_free * np.ones([10801, 1])
        self.rs_demand = Globalvar.demand_ramp[0] * np.ones([10801, 1])
        self.capacity_measure_d1 = np.zeros((1, 3))
        self.capacity_measure_d2 = np.zeros((1, 3))
        self.capacity_measure_d3 = np.zeros((1, 3))
        # time

    @staticmethod
    def loadedvehicle(self):
        # loaded vehicles list
        return self.av

    def speed_contour(self, di, location, t_begin, t_end):
        speed = float(get_attrvalue(di, 'harmonicMeanSpeed'))
        self.speed_contour_matrix[location, t_begin:t_end] = speed

    def asm(self, detect_time, detect_dist):
        speed_matrix = self.speed_contour_matrix
        detect_node = list()
        for i in range(len(detect_dist)):
            for j in range(len(detect_time)):
                detect_node.append([detect_dist[i], detect_time[j]])
        theta = 50  # distance filter
        tau = 15  # time filter
        c_free = 70 / 3.6  # m/s
        c_cong = -15 / 3.6  # m/s
        v_thr = 60 / 3.6  # m/s crossover speed
        delta_v = 20 / 3.6  # m/s transfer width speed
        N_cong = np.zeros([self.total_length + 1, self.total_time + 1])
        N_free = np.zeros([self.total_length + 1, self.total_time + 1])
        zeta_cong = np.zeros([self.total_length + 1, self.total_time + 1])
        zeta_free = np.zeros([self.total_length + 1, self.total_time + 1])
        w = np.zeros([self.total_length + 1, self.total_time + 1])
        for d in range(1, self.total_length + 1):
            for t in range(1, self.total_time + 1):
                print("process is:", (t * d) / (self.total_time * self.total_length))
                if (d not in detect_dist) and (d % 10 == 0) and (t in detect_time):
                    for i in range(len(detect_node)):
                        detect_d = detect_node[i][0]
                        detect_t = detect_node[i][1]
                        theta_free = math.exp(-abs(detect_d - d) / theta - abs(detect_t - t -
                                                                               (detect_d - d) / c_free) / tau)
                        theta_cong = math.exp(-abs(detect_d - d) / theta - abs(detect_t - t -
                                                                               (detect_d - d) / c_cong) / tau)
                        zeta_free[d, t] += theta_free * speed_matrix[detect_d][detect_t]
                        zeta_cong[d, t] += theta_cong * speed_matrix[detect_d][detect_t]
                        N_cong[d, t] += theta_cong
                        N_free[d, t] += theta_free
                    zeta_free[d, t] = zeta_free[d, t] / N_free[d, t]
                    zeta_cong[d, t] = zeta_cong[d, t] / N_cong[d, t]
                    v_star = min(zeta_cong[d, t], zeta_free[d, t])
                    w[d, t] = 0.5 * (1 + np.tanh((v_thr - v_star) / delta_v))
                    index_t = detect_time.index(t)
                    harm_speed = w[d, t] * zeta_cong[d, t] + (1 - w[d, t]) * zeta_free[d, t]
                    if harm_speed < 0:
                        harm_speed = -1
                    speed_matrix[d - 10:d, detect_time[index_t - 1]:t] = harm_speed

    def demand(self):
        self.ms_demand[Globalvar.peak_time[0][0]:Globalvar.peak_time[0][1]] = \
            self.ms_demand[Globalvar.peak_time[1][0]:Globalvar.peak_time[1][1]] = Globalvar.demand_main_peak
        self.rs_demand[(Globalvar.peak_time[1][0] + Globalvar.on_ramp_lag):
                       (Globalvar.peak_time[1][1] + Globalvar.on_ramp_lag)] = Globalvar.demand_ramp[1]

    def capacity(self, di, det_id):
        if det_id == 'l2_11' or det_id == 'l3_3' or det_id == 'l3_21':
            det_data = np.zeros((1, 3))
            speed = float(get_attrvalue(di, 'harmonicMeanSpeed'))
            flow = float(get_attrvalue(di, 'flow'))
            density = float(get_attrvalue(di, 'occupancy'))
            det_data[0, 0] = speed
            det_data[0, 1] = flow
            det_data[0, 2] = density
            if det_id == 'l2_11':
                self.capacity_measure_d1 = np.vstack((self.capacity_measure_d1, det_data))
            elif det_id == 'l3_3':
                self.capacity_measure_d2 = np.vstack((self.capacity_measure_d2, det_data))
            else:
                self.capacity_measure_d3 = np.vstack((self.capacity_measure_d3, det_data))

    def capacity_drop(self):
        flow_free = list()
        flow_cong = list()
        speed_limit = Globalvar.speed_limit
        capacity_measure = np.array([self.capacity_measure_d1, self.capacity_measure_d2, self.capacity_measure_d3])
        for record in range(capacity_measure.shape[1]):
            if capacity_measure[0, record, 0] >= speed_limit * 0.75:
                flow_free.append(capacity_measure[1, record, 1])
            elif capacity_measure[0, record, 0] > 0:
                flow_cong.append(capacity_measure[2, record, 1])
        merge_capacity = max(flow_free)
        queue_resolve = sum(flow_cong) / len(flow_cong)
        capacity_drop = merge_capacity - queue_resolve
        return capacity_measure, capacity_drop

    def plot(self, capacity_measure):
         # speed contour plot
        step = 1
        y = np.arange(0, self.total_length + 1, step)
        x = np.arange(0, self.total_time + 1, step)
        X, Y = np.meshgrid(x, y)
        # pdb.set_trace()
        speed = self.speed_contour_matrix
        cset = plt.contourf(X, Y, speed, cmap=plt.cm.hot)
        plt.xlabel('time(s)')
        plt.ylabel('distance(m)')
        plt.title('speed contour')
        plt.colorbar(cset)
        plt.savefig("speed_contour.jpg")
        pdb.set_trace()
        plt.show()
        #  demand plot
        plt.plot(x, self.ms_demand, 'g--', label='mainstream demand')
        plt.plot(x, self.rs_demand, 'b--', label='on-ramp demand')
        plt.plot(x, self.ms_demand + self.rs_demand, 'r-', label='total demand')
        plt.title('traffic demand')
        plt.xlabel('time(s)')
        plt.ylabel('volume(veh/h)')
        plt.legend()
        plt.savefig("demand.jpg")
        plt.show()
        #  fundamental diagram and capacity drop
        pdb.set_trace()
        x = capacity_measure[0, :, 2]
        y = capacity_measure[0, :, 1]
        plt.scatter(x, y, alpha=0.6)
        plt.xlabel('density')
        plt.ylabel('flow')
        plt.title('density-flow')
        plt.savefig("fd.jpg")
        plt.show()

    def result_file(self):
        det_data = xmld.parse('data/cross.out')
        root = det_data.documentElement
        det_intervals = get_xmlnode(root, 'interval')
        detect_timenode = [0]
        detect_location = [0]
        # demand matrix
        self.demand()
        # read detector data
        for di in det_intervals:
            det_id = get_attrvalue(di, 'id')  # id
            id_list = det_id.split('_')
            road_id = id_list[0]  # road id
            if road_id != 'l2':  # for road has two lanes
                det_index = int(id_list[1])
            else:
                det_index = int(id_list[1][1])
            t_begin = int(float(get_attrvalue(di, 'begin')))  # period begin time
            t_end = int(float(get_attrvalue(di, 'end')))  # period end time
            detect_timenode.append(t_end)  # detect time list for later use
            location = Globalvar.det_location[road_id][det_index - 1]  # detect location
            detect_location.append(location)  # detect location list for later use
            self.speed_contour(di, location, t_begin, t_end)
            self.capacity(di, det_id)
        detect_time = sorted(set(detect_timenode))
        detect_dist = sorted(set(detect_location))
        capacity_measure, capacity_drop = self.capacity_drop()
        if Globalvar.asm == 1:
            self.asm(detect_time, detect_dist)
        self.plot(capacity_measure)
#        return doc

if __name__ == '__main__':
    aaa = Result(1, 14135)
    aaa.result_file()
