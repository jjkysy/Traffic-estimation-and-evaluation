from __future__ import absolute_import
from __future__ import print_function

import os
import sys

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
import Globalvar
import pdb

# ====================================================================================================
# data generation
# ====================================================================================================
def generate_routefile():
    optnr = 4  # optimal platoon size
    p_rate_main = Globalvar.p_rate_main
    p_rate_ramp = Globalvar.p_rate_ramp
    dm_free = Globalvar.demand_main_free  # total car
    dm_peak = Globalvar.demand_main_peak  # av num
    dr_free = Globalvar.demand_ramp[0]  # total car
    dr_peak = Globalvar.demand_ramp[1]  # av num
    dm_av_free = int(dm_free * p_rate_main)
    dm_av_peak = int(dm_peak * p_rate_main)
    dr_av_free = int(dr_free * p_rate_ramp)
    dr_av_peak = int(dr_peak * p_rate_ramp)
    dm_hm_free = dm_free - dm_av_free
    dm_hm_peak = dm_peak - dm_av_peak
    dr_hm_free = dr_free - dr_av_free
    dr_hm_peak = dr_peak - dr_av_peak
    peak_time_start1 = Globalvar.peak_time[0][0]
    peak_time_start2 = Globalvar.peak_time[1][0]
    peak_time_end1 = Globalvar.peak_time[0][1]
    peak_time_end2 = Globalvar.peak_time[1][1]
    # make tests reproducible
    with open("data/cross1.rou.xml", "w") as routes:
        print("""<routes> 
        <vType id="auto" color = "1,0,0" accel="0.8" decel="4.5" length="5" minGap="2.0" maxSpeed="22" 
        carFollowModel='IDM' tau='1.6' speedDev='0'/>
      
        <vType id="human" color="0,1,0" accel="0.8" decel="4.5" length="5" minGap="2.0" maxSpeed="22" 
        carFollowModel='IDM' tau='1.6' speedDev='0'/>""", file=routes)
#   main stream flow
        print(
            '''   
        <flow id="maf1" from="l0" to="l3" begin="%i" end="%i" vehsPerHour="%i" departSpeed = "max" type="auto"/>
            
        <flow id="mhf1" from="l0" to="l3" begin="%i" end="%i" vehsPerHour="%i" departSpeed = "max" type="human"/>'''
            % (0, peak_time_start1, dm_av_free, 0, peak_time_start1, dm_hm_free), file=routes)
        print(
            '''
        <flow id="raf1" from="lm" to="l3" begin="%i" end="%i" vehsPerHour="%i" departSpeed = "max" type="auto"/>

        <flow id="rhf1" from="lm" to="l3" begin="%i" end="%i" vehsPerHour="%i" departSpeed = "max" type="human"/>'''
            % (0, peak_time_start2+Globalvar.on_ramp_lag, dr_av_free, 0, peak_time_start2+Globalvar.on_ramp_lag,
               dr_hm_free), file=routes)
        print(
            ''' 
        <flow id="map1" from="l0" to="l3" begin="%i" end="%i" vehsPerHour="%i" departSpeed = "max" type="auto"/>

        <flow id="mhp1" from="l0" to="l3" begin="%i" end="%i" vehsPerHour="%i" departSpeed = "max" type="human"/>'''
            % (peak_time_start1, peak_time_end1, dm_av_peak, peak_time_start1, peak_time_end1, dm_hm_peak), file=routes)
        print(
            '''
        <flow id="maf2" from="l0" to="l3" begin="%i" end="%i" vehsPerHour="%i" departSpeed = "max" type="auto"/>

        <flow id="mhf2" from="l0" to="l3" begin="%i" end="%i" vehsPerHour="%i" departSpeed = "max" type="human"/>'''
            % (peak_time_end1, peak_time_start2, dm_av_free, peak_time_end1, peak_time_start2, dm_hm_free),
            file=routes)
        print(
            '''
        <flow id="map2" from="l0" to="l3" begin="%i" end="%i" vehsPerHour="%i" departSpeed = "max" type="auto"/>

        <flow id="mhp2" from="l0" to="l3" begin="%i" end="%i" vehsPerHour="%i" departSpeed = "max" type="human"/>'''
            % (peak_time_start2, peak_time_end2, dm_av_peak, peak_time_start2, peak_time_end2, dm_hm_peak), file=routes)
        print(
            '''
        <flow id="rap1" from="lm" to="l3" begin="%i" end="%i" vehsPerHour="%i" departSpeed = "max" type="auto"/>

        <flow id="rhp1" from="lm" to="l3" begin="%i" end="%i" vehsPerHour="%i" departSpeed = "max" type="human"/>'''
            % (peak_time_start2 + Globalvar.on_ramp_lag, peak_time_end2 + Globalvar.on_ramp_lag, dr_av_peak,
               peak_time_start2 + Globalvar.on_ramp_lag, peak_time_end2 + Globalvar.on_ramp_lag,
               dr_hm_peak), file=routes)
        print(
            '''
        <flow id="maf3" from="l0" to="l3" begin="%i" end="%i" vehsPerHour="%i" departSpeed = "max" type="auto"/>

        <flow id="mhf3" from="l0" to="l3" begin="%i" end="%i" vehsPerHour="%i" departSpeed = "max" type="human"/>'''
            % (peak_time_end2, Globalvar.demand_time, dm_av_free, peak_time_end2, Globalvar.demand_time, dm_hm_free),
            file=routes)
        print(
            '''
        <flow id="raf2" from="lm" to="l3" begin="%i" end="%i" vehsPerHour="%i" departSpeed = "max" type="auto"/>

        <flow id="rhf2" from="lm" to="l3" begin="%i" end="%i" vehsPerHour="%i" departSpeed = "max" type="human"/>'''
            % (peak_time_end2+Globalvar.on_ramp_lag, Globalvar.demand_time, dr_av_free,
               peak_time_end2+Globalvar.on_ramp_lag, Globalvar.demand_time, dr_hm_free), file=routes)
        print("</routes>", file=routes)
        # pdb.set_trace()