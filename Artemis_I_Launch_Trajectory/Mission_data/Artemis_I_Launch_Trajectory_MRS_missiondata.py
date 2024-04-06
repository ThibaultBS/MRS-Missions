#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 11 10:56:45 2024

@author: thibault
"""

import numpy as np
import pandas as pd
import datetime


# guidance frame IDs / DO NOT change these variables
F_Earth_ENU_abs = 1
F_EFvel_Earth_ENU_delta = 2
F_SFvel_Earth_ENU_delta = 3
F_Launch_ENU_abs = 4
F_GCRF_abs = 5
F_VUW_abs = 6
F_VNB_abs = 7
F_none = 10

class MRSmissionData():
    
    # Mission name: this name will be used for display and for the filenames 
    # of mission and event data frames. Can be any kind of string.
    name = 'Artemis 1'
    
    # The launchtype defines from where the trajectory starts:
    #   - launchtype 0: propagation starts from ICRF state vector (defined below)
    #   - launchtype 1: rocket sits on launchpad (position defined below)
    #
    launchtype = 1 
    
    # t0 is the initial reference time. It can be provided as Julian Date TDB
    # (JD TBD) or as UTC time. 
    # 
    # The use of the reference time depends from the chosen launch type. In case of:
    #   - launchtype 0: t0 is the time of the initial state vector y0 (see below);
    #                   If t0_JD>0, it is used. Otherwise, t0_UTC is used.
    #   - launchtype 1: t0 is the time at which MET (mission ellapsed time) = 0;
    #                   t0_UTC is always used, t0_JD is ignored
    t0_JD = 0 # JD TDB 
    t0_UTC = datetime.datetime.fromisoformat('2022-11-16T06:47:44.000') # UTC
   

    # t0_MET defines the MET-value at the moment of t0_JD/t0_UTC. Default is 0.
    # The use depends from the launchtype:
    #   - launchtype 0: value is used as provided
    #   - launchtype 1: value is set to 0; for launches MET=0 for given t0_UTC
    t0_MET = 0. # MET seconds
    
    # It might be helpful to stop the mission at at time earlier than the 
    # MET-value in the last row of the mission segments (see below), e.g. to
    # conduct just a short flight to test new parameters.
    # The propagation is terminated at the given tend_MET time (if tend_MET != 0)
    tend_MET = 8048 # MET seconds
 
    # In case of launchtype 1, a launchsite needs to be provided.
    # The launchsite_name can be any kind of string and is used for display only.
    # The launchsite_LLA is the actual latitude, longitude, and altitude of the
    # launchsite.
    #
    # MRS 1.0/1.1 does not support launches, this data is therefore only used
    # to calculate the range (ground distance to launchsite).
    launchsite_name = 'Kennedy Space Center Launch Complex 39B'
    launchsite_LLA = np.array([28.627222, -80.620833, 30.])  # [deg, geodetic], [deg], [m]
    
    integrator_atol = 1e-5 # solve_ivp atol value [m]; default: 1e-9
    integrator_rtol = 1e-5 # solve_ivp rtol value; default: 1e-9
    
   
    missionSegments = pd.DataFrame([
                    [-10.,    0,      0,        'Start of simulation'],
                    [0.2,     0,      1,        'Liftoff'],
                    [6300,    0,      2,        'Coasting'],
                    [7500,    1,      0,        'Orion/ICPS spring separation'], 
                    [7581,    1,      1,        'USS maneuver'], 
                    [445000,  0,      1,        'End of simulation'], 
                    ], 
           columns= ['MET','type','configID', 'comment'])
    
    propaSettings = pd.DataFrame([ 
                    [0,     '-',       1,            0,        10,     'Fix on test stand'],
                    [1,     'DOP853',  1,            0,        10,     'Flight with active SC'],
                    [1,     'DOP853',  1,            1,        10,     'Flight coasting'],
                    ], 
           columns= ['mode','method','stepsizePropa','forcesID','downsampleLog','comment'])
   
    forcesSettings = pd.DataFrame([
                    [35,     0,  ['Earth'], 'nrlmsise00',1, 0, 0, 0, 1,  'SH35, Earth Atmos, active SC'],
                    [35,     0,  ['Earth'], '', 0, 0, 0, 0, 0, 'SH35, no atmos, static SC'],
                    ], 
           columns= ['EarthSHn','MoonSHn','planets','atmosModel','drag','SRP', 'EarthTides', 'MoonTides', 'activeSC', 'comment'])
    
    maneuverSettings = pd.DataFrame([
                    ['VNB',    0.230,    0, 0,     [0,0], 'Earth',   'Spring separation from ICPS'],
                    ['VNB',    1.676,    0, 0,     [0,0], 'Earth',   'Upper stage separation (USS) maneuver']
                    ],
            columns = ['frame', 'dx', 'dy', 'dz', 'args', 'planet', 'comment'])
    
    missionEvents = pd.DataFrame([
                   [0.2, 'Lift-off'],
                   [500, 'Orbit insertion.'],
                   [3222, 'End PRM'],
                   [7500, 'Staging ICPS'],
                   [8046.8, 'RSV']
                   ],
            columns = ['MET', 'eventType'])
    
    class guidanceData():
        """
        
        The following frames are available for both elevation/declination and
        heading angle/right ascension. 
        
        F_Earth_ENU_abs: 
            - Absolute angle values.
            - Earth-bound East/North/Up frame (using round shape of Earth).
            - Can be combined with: 
                - F_Earth_ENU_abs
                - F_EFvel_Earth_ENU_delta
                - F_SFvel_Earth_ENU_delta
            - Used to point the spacecraft in a fixed direction relative to
              local topocentric ENU frame.
            - Angle definitions:
                - Elevation: angle from EN-plane towards U-vector 
                - Heading: clockwise angle from N-vector (compass)
              
        F_EFvel_Earth_ENU_delta  
            - Delta values to the Earth-fixed velocity vector, expressed in 
              local ENU frame.
            - Can be combined with:
                - F_Earth_ENU_abs
                - F_EFvel_Earth_ENU_delta
                - F_SFvel_Earth_ENU_delta
            - Used for drag free gravity turns during rocket launches.
            - Angle definitions:
                - Elevation: delta value to ENU elevation of Earth-fixed velocity.
                - Heading: delta value to ENU heading of Earth-fixed velocity.
                
        F_SFvel_Earth_ENU_delta
            - Delta values to the inertial velocity vector, expressed in local
              ENU frame.
            - Can be combined with:
                - F_Earth_ENU_abs
                - F_EFvel_Earth_ENU_delta
                - F_SFvel_Earth_ENU_delta
            - Used to point the rocket relatively to its velocity vector in
              local topocentric ENU frame.
            - Angle definitions:
                - Elevation: delta value to ENU elevation of space-fixed velocity.
                - Heading: delta value to ENU heading of space-fixed velocity.
        
        F_Launch_ENU_abs
            - Absolute angle values.
            - Inertially fixed ENU frame defined at time and place of launch.
            - Elevation F_Launch_ENU_abs can be combined with Heading in: 
                - F_Earth_ENU_abs
                - F_EFvel_Earth_ENU_delta
                - F_SFvel_Earth_ENU_delta
                - F_Launch_ENU_abs
            - Heading F_Launch_ENU_abs can be combined with Elevation in: 
                - F_Launch_ENU_abs
            - Used for pitch maneuvers of rocket launches (during whole ascent
              or ahead of gravity turns).
            - Angle definitions:
                - Elevation: angle from U-vector towards EN-plane (pitch angle)
                - Heading: clockwise angle from N-vector (compass).
        
        F_GCRF_abs
            - Absolute angle values.
            - GCRF frame (E=x, N=y, U=z).
            - Cannot be combined with other frames.
            - Used for inertially fixed maneuvers without a specific frame.
            - Angle definitions:
                - Elevation: declination, measured from xy-plane towards z-vector.
                - Heading: right ascension, measured CCW from x- to y-vector.
              
        F_VUW_abs
            - Absolute angle values.
            - VUW frame:
                - V (E, x) = velocity direction
                - U (N, y) = W x V
                - W (U, z) = V x r (r=position vector), direction of normal to 
                  orbital plane.
            - Cannot be combined with other frames.
            - Used for delta-v maneuvers
            - Angle definition:
                - Elevation: declination, measured from VU-plane towards W-vector.
                - Heading: right ascension, measured CCW from V- to U-vector.
        
        F_VNB_abs
            - Absolute angle values.
            - VUW frame:
                - V (E, x) = velocity direction
                - N (N, y) =  r x V (r=position vector), direction of normal to 
                  orbital plane.
                - B (U, z) = V x N
            - Cannot be combined with other frames.
            - Used for delta-v maneuvers
            - Angle definition:
                - Elevation: declination, measured from VN-plane towards B-vector.
                - Heading: right ascension, measured CCW from V- to N-vector.
    
        F_none
            - No frame in use.
            - Angle values for elevation and heading are ignored.
            - Guidance vector direction equals to velocity vector direction
            - Cannot be combined with other frames.
            - Used for long burns along the trajectory of the spacecraft.
     
        
        F_SM0_abs - F_SM9_abs
            - Absolute angle values.
            - Manually set up intertial frames (e.g. for REFSMMAT).
            - Cannot be combined with other frames.
            - Used for delta-v maneuvers
            - Angle definition:
                - Elevation: declination, measured from VU-plane towards W-vector.
                - Heading: right ascension, measured CCW from V- to U-vector.
         
        """
        
        # name of the guidance; string; only used for displayy
        name = 'Artemis 1 Guidance'

        
        gElevTab = np.array([
            [-10,     F_Launch_ENU_abs,     0.0], # 
            [0,       F_Launch_ENU_abs,     0.0], # 
            [6,       F_Launch_ENU_abs,     2.3820], # pitch SC  
            [16,      F_EFvel_Earth_ENU_delta,  0], # align to vrel
            [23,      F_EFvel_Earth_ENU_delta, 0], # now aligned to vrel
            [132,     F_Launch_ENU_abs,     56.578125], # align to launch ENU pitch # 57 / 55.536
            [142,     F_Launch_ENU_abs,     95.09375], # slowly increase pitch angle + 94 / 95.4# TODO should be rather 142 seconds
            [485,     F_SFvel_Earth_ENU_delta, 0], # align to inertial vel
            [500,     F_SFvel_Earth_ENU_delta,  0], # now aligned to inertial vel
            [5000,    F_VNB_abs,           -0.37037037 ],
            [5200,    F_VNB_abs,            0.7777777],
            [6293,    F_none,               0]
           
            ])
        
        
        gHeadTab = np.array([
            [-10,   F_Launch_ENU_abs,        0], #
            [0,     F_Launch_ENU_abs,        75.], # 
            [6,     F_Launch_ENU_abs,        75.], # 
            [16,    F_EFvel_Earth_ENU_delta, 0], # align to vrel
            [23,    F_EFvel_Earth_ENU_delta, 0], # now aligned to vrel
            [132,   F_SFvel_Earth_ENU_delta, 0], # align to inertial vel
            [531.8, F_SFvel_Earth_ENU_delta, 0], # now aligned to inertial vel 
            [5000,  F_VNB_abs,               0.],
            [5200,  F_VNB_abs,               0.],
            [6293,  F_none,                  0]
            ])

  
    class spacecraft():
        
        # name of spacecraft
        name = 'Artemis I'
        
        # list of spacecraft elements 
        SCelements = np.array([
                        ['SRB', 2],
                        ['Stages', 1],
                        ['Payload', 1]
                        ], dtype=object)  
        
        # define optional static values used for fast trajectory computations
        class staticValues():
            mass = 99337. # [kg]
            dragarea = 10.81 # [m^2]
            Cd = 2.40 
            Cr = 1.80
            SRParea = 0
           
        class SRB():
             
             name = 'SLS SRB'  
             
             partsInit = np.array([
                             # name, stagingTime, dryMass,     fuelMass,  dragArea
                             ['SRB',  132.,       99337,     626411, 10.81],
                            ], dtype=object)  
             
             engines = np.array([
                                # name,  description,  thrust SL, thrust VAC, fuel flow 100% 
                                 ['SRB', 'SRB', 14107703, 15815811,    6050.6],
                                 ], dtype=object) 
           
             throttleInit = np.array([
                             # MET    Start   End     EngineType  EngineAmount,   Description
                             [-10,      0.0,    -1,   0,          1,   ''],     
                             [0,        0.0,    -1,   0,          1,   'Ignition!'],    
                             [0.3,      1.0,    -1,   0,          1,   ''],     
                             [3.2,      0.985,  -1,   0,          1,   ''],      
                             [6.3,      0.994,  -1,   0,          1,   ''],      
                             [23.4,     0.998,  -1,   0,          1,   ''],      
                             [26.4,     0.949,  -1,   0,          1,   ''],      
                             [35.,      0.859,  -1,   0,          1,   ''],      
                             [43.,      0.807,  -1,   0,          1,   ''],      
                             [52.5,     0.790,  -1,   0,          1,   ''],      
                             [70.,      0.885,  -1,   0,          1,   ''],      
                             [80.,      0.923,  -1,   0,          1,   ''],      
                             [88.5,     0.924,  -1,   0,          1,   ''],      
                             [94.5,     0.894,  -1,   0,          1,   ''],      
                             [98.7,     0.854,  -1,   0,          1,   ''],      
                             [100.8,    0.817,  -1,   0,          1,   ''],      
                             [106.,     0.792,  -1,   0,          1,   ''],      
                             [110.,     0.756,  -1,   0,          1,   ''],      
                             [113.,     0.699,  -1,   0,          1,   ''],      
                             [116.,     0.499,  -1,   0,          1,   ''],      
                             [119,      0.220,  -1,   0,          1,   ''],      
                             [124.,     0.040,  -1,   0,          1,   ''],      
                             [126.2,    0.0,    -1,   0,          0,   'SRB are off.'],      
                             ], dtype=object) 
        
             # Drag Coeffient 
             C_D = np.array([
                         # Random drag coeff, no reference! 
                         #   Mach    CD AOA 0°
                         [   0.,     0.25],
                         [   0.15,   0.25],
                         [   0.65,   0.29],
                         [   0.8,    0.33],
                         [   1.25,   0.62],
                         [   1.40,   0.62],
                         [   3.50,   0.32],
                         [   5.00,   0.26],
                         [   8.70,   0.24],
                         [   9.00,   0.24],
                         [  10.00,   0.24]])     
            
        class Stages():
             
             name = 'SLS stages'  
             
             partsInit = np.array([
                             # name, stagingTime, dryMass,     fuelMass,  dragArea
                            ['Core Stage',  500.,     103871,   987471, 55.42],
                            ['ICPS',       7500.,       5171,    28987, 20.43],
                            ['ESM',      999999.,       4400,     8600,  0.0],
                            ], dtype=object)  
             
             engines = np.array([
                                # name,  description,  thrust SL, thrust VAC, fuel flow 100% 
                                 ['RS-25',  '-', 1705.8e3, 2090.7e3,    471.34],
                                 ['RL10B-2','-', 110093.,  110093.,     24.117 ],
                                 ['OMS-E',  '-', 26689.,   26689.,      8.612],
                                 ], dtype=object) 
           
            
             throttleInit = np.array([
                               # MET    Start   End     EngineType  EngineAmount,   Description  
                              # Time,     Stage,  ActEngines, Throttle,   Mode,   Gradient
                             [-10,       0.,      0.,     0,       4,  ''   ],     # Sim Start
                             [-6.6,      0.,     -1,      0,       4,  'Engines start!'   ],  
                             [-2.35,     1.,      1.,     0,       4,  ''   ],      # time optimized to get right usage of fuel prior to lift off
                             [0,         1.09,    1.09,   0,       4,  ''   ],  
                             [55,        1.00,    1.00,   0,       4,  'Throttle down for max-Q.'   ],  
                             [81,        1.09,    1.09,   0,       4,  'Throttle up.'   ],  
                             [123,       0.85,    0.85,   0,       4,  'Throttle down for SRB separation.'   ],  
                             [132,       1.09,    1.09,   0,       4,  'Throttle up.'   ],  
                             [421,       1.09,   -1,      0,       4,  'Limit max. G'   ],  
                             [440,       0.949,  -1,      0,       4,  ''   ],  
                             [460,       0.820,   0.729,  0,       4,  ''   ],  
                             [476,       0.67,    0.67,   0,       4,  ''   ],  
                             [482.8,     0.,      0.,     0,       4,  'Engines off.'   ],  
                             
                             [3200,      1.,       1.,    1,       1,  'Start PRM.'   ],
                             [3221.28,   0,        0.,    1,       1,  'End PRM.'   ],
                             
                             [5220.5,      1.,       1.,    1,       1,  'Start TLI.'   ], 
                             [6293,     0,        0.,    1,       1,  'End TLI.'   ]
                             ], dtype=object) 
        
        
             # Drag Coeffient 
             C_D = np.array([
                         # Random drag coeff, no reference! 
                         #   Mach    CD AOA 0°
                         [   0.,     0.25],
                         [   0.15,   0.25],
                         [   0.65,   0.29],
                         [   0.8,    0.33],
                         [   1.25,   0.62],
                         [   1.40,   0.62],
                         [   3.50,   0.32],
                         [   5.00,   0.26],
                         [   8.70,   0.24],
                         [   9.00,   0.24],
                         [  10.00,   0.24]])     
             
             
             
        class Payload():
              
              name = 'Orion Spacecraft'  
              
              partsInit = np.array([
                              # name,            stagingTime, dryMass,  fuelMass,  dragArea
                             ['Fairing panels',         200.,  1270.0,   0, 0],
                             ['Launch Abort System',    225.,  7575.0,   0, 0],
                             ['Crew Module',         999999.,  9344.0,   0, 0],
                             ], dtype=object)  
              
 