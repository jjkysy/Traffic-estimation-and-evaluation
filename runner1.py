#!/usr/bin/env python
"""
@file    runner1_try.py
@author  yao
SUMO, Simulation of Urban MObility; see http://sumo.dlr.de/
Copyright (C) 2009-2017 DLR/TS, Germany
latest version
"""
from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import optparse
import random
import Globalvar
import tl_c as tlc
# import numpy as np
import generate_routefile as gen_route
# from collections import OrderedDict

try:
    sys.path.append(os.path.join(os.path.dirname(
        __file__), '..', '..', '..', '..', "tools"))  # tutorial in tests
    sys.path.append(os.path.join(os.environ.get("SUMO_HOME", os.path.join(
        os.path.dirname(__file__), "..", "..", "..")), "tools"))  # tutorial in docs
    from sumolib import checkBinary  # noqa
except ImportError:
    sys.exit(
        "please declare environment variable 'SUMO_HOME' as the root directory of your sumo installation (it should"
        " contain folders 'bin', 'tools' and 'docs')")
# import tl_c as tlc
# we need to import python modules from the $SUMO_HOME/tools directory
import traci
import pdb
import result
# ====================================================================================================
# control main
# ====================================================================================================
def run():
    """execute the TraCI control loop"""
    # initialize indices
    simstep = 0
    # optnr = Globalvar.optnr
    # tldcum = OrderedDict()  # time point of passing tlc decision point
    ldcar = list()  # tuple of CAV
    av_list = list()
    occupancy = 0
    # phasetime = 0  # initial phase time
    # platoon_size = dict()  # dict of: {leader_id: platoon_tailed_id}
    # tl_lastswitch = dict()
    # we start with phase 2 where EW has green
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        if simstep >= 1400: pdb.set_trace()
        # create ldcar:list of running auto cars
        try:
            depart_id = traci.simulation.getDepartedIDList()[0]
        except IndexError:
            pass
        else:
            if traci.vehicle.getTypeID(depart_id) == 'auto':
                ldcar.extend([depart_id])
                av_list.extend([depart_id])
        arrived_list = list(traci.simulation.getArrivedIDList())
        if arrived_list:
            ldcar_set = set(ldcar) - set(arrived_list)
            ldcar = list(ldcar_set)
        if Globalvar.ramp_metering == 1:
            # alinea
            tl_id = '2'
            tl_control = tlc.TrafficLight(tl_id, simstep)
            # pdb.set_trace()
            occupancy = tl_control.alinea(occupancy)
        simstep += 1
        print(simstep)
        # print(plplan)
    traci.close()
    sys.stdout.flush()
    # return dist, v, leadingmatrix, ldcar, carcum, testav, merge_cum, split_cum
    return av_list, simstep

def get_options():
    optParser = optparse.OptionParser()
    optParser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    options, args = optParser.parse_args()
    return options


def main():
    # this is the main entry point of this script
    # entry sumo
    random.seed(666)
    sumoBinary = checkBinary('sumo-gui')  # skip the choosing part
    # set timestep and random seed
    time_step = 0.1
    # set global variables and input data
    # first, generate the route file for this simulation
    gen_route.generate_routefile()
    pdb.set_trace()
    # vehNr = Globalvar.nrtotal
    traci.start([sumoBinary, "-c", "data/cross1.sumocfg", "--step-length", str(time_step),
                 "--tripinfo-output", "tripinfo.xml", "--time-to-teleport", "1000"])
    # main function
    av_list, simstep = run()
    pdb.set_trace()
    rt = result.Result(av_list, int(simstep*time_step))
    rt.result_file()




if __name__ == '__main__':
    main()
