#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar  2 17:12:17 2024

@author: thibault
"""

from myrocketsimulator import MRSlib, MRSvislib
import numpy as np
import matplotlib.pyplot as plt


"""
Mission description

This mission recreates the flight of Artemis I launched in 2022 from lift-off
to some later point in the flight (Reference State Vector, RSV). The RSV was
extracted from publicly available trajectory data of Artemis I on JPL Horizons.

The paper [1] describes in the detail how the trajectory was reconstructed and
provides results generated with this mission.

Mission output:
    - Mission dataframe (Artemis 1_missionDF.csv)
    - Events dataframe (Artemis 1_eventsDF.csv)
    - Google Earth kml file (Artemis 1 Earth_Orbit.kml)
    - Inertial trajectory in 3D representation (EarthOrbitGCRF.svg)
    - Orbital Elements in Earth orbit (EarthOE.svg)
    - Ground track on Earth (EarthGroundTrack.svg)

References: 
[1] Bautze-Scherff, Thbiault, 2024
    Artemis I Launch Trajectory Reconstruction with the MyRocketSimulator Python Package
    https://www.researchgate.net/publication/379605796_Artemis_I_Launch_Trajectory_Reconstruction_with_the_MyRocketSimulator_Python_Package

"""

# load and perform mission
missionname = './Mission_Data/Artemis_I_Launch_Trajectory_MRS_missiondata.py'
missionObject = MRSlib.MRSmission(missionname, checkmission=False)
missionObject.check_MD()
missionObject.run_mission()

# add special events
missionObject.get_EventsList(eventNames=['Mach1','MaxQ'])

# add values to mission data frame
missionObject.expand_DFname(['EarthApoPeri'])
missionObject.expand_DFname(['EarthLLA'])
missionObject.expand_DFname(['EarthOrbElements'])

# add values to event data frame
missionObject.expand_DFname(['EarthLLA'], DFname='eventsDF')
missionObject.expand_DFname(['EarthFPAHAvel'], DFname='eventsDF')
missionObject.expand_DFname(['EarthFixedFPAHAvel'], DFname='eventsDF')
missionObject.expand_DFname(['EarthOrbElements'], DFname='eventsDF')
missionObject.expand_DFname(['EarthApoPeri'], DFname='eventsDF')
missionObject.expand_DFname(['RangeToLaunchsite'], DFname='eventsDF')

# generate MRS vision object
visionObject = MRSvislib.MRSviewer(missionObject)

# show values at SRB staging
visionObject.print_EventDetails(np.array(['SLS SRB terminated: Staging of SRB.']), np.array(['EarthAlt']))

# show values at Orbit Insertion (OI)
visionObject.print_EventDetails(np.array(['Orbit insertion.']), np.array(['EarthOESMA','EarthOEinclination','EarthVEL', 'EarthOEargPeriapsis']))
visionObject.print_EventDetails(np.array(['Orbit insertion.']), np.array(['Apogee','Perigee','EarthAlt','EarthOERAAN']))

# show values after PRM
visionObject.print_EventDetails(np.array(['End PRM']), np.array(['Apogee','Perigee','EarthAlt','EarthOERAAN']))

# show values at RSV
visionObject.print_EventDetails(np.array(['RSV']), np.array(['Apogee','Perigee','EarthOEinclination']))
visionObject.print_EventDetails(np.array(['RSV']), np.array(['EarthOEargPeriapsis','EarthOEtrueAnomaly','EarthOERAAN']))
visionObject.print_EventDetails(np.array(['RSV']), np.array(['EarthOEeccentricity','EarthOESMA','EarthAlt']))

# define events for table 13 of [1]
eventList = np.array([
    'Lift-off',
    'Mach1',
    'MaxQ',
    'SLS SRB terminated: Staging of SRB.',
    'Orion Spacecraft: Staging of Launch Abort System.',
    'SLS stages: Engines off.',
    'Orbit insertion.',
    'SLS stages: Start PRM.',
    'SLS stages: End PRM.',
    'SLS stages: Start TLI.',
    'SLS stages: End TLI.',
    'Staging ICPS',
    'RSV'
     ])

# define values for table 13 of [1]
eventValues = np.array([
    'EarthAlt',
    'EarthFixedVEL',
    'EarthFixedFPA',
    'EarthFixedHA',
    'EarthVEL',
    'EarthFPA',
    'EarthHA',
    ])

# show values for table 13 of [1]
visionObject.print_EventDetails(eventList, eventValues)

# Export Google Earth trajectory
visionObject.export_Earth_KML(folder='./Mission_output/')

# show and save 3d trajectory in inertial frame
fig3D, ax3D = visionObject.plot_GCRF_orbit()
fig3D.savefig('./Mission_output/EarthOrbitGCRF.svg', dpi=300)

# show and save orbital elements in Earth's orbit
figEarthOE, axEarthOE = visionObject.plot_EarthOE()
figEarthOE.savefig('./Mission_output/EarthOE.svg', dpi=300)

# show and save ground track on Earth
figEarthGroundtrack, axEarthGroundtrack = visionObject.plot_GroundtrackEarth()
figEarthGroundtrack.savefig('./Mission_output/EarthGroundTrack.svg', dpi=300)

# export data frames
missionObject.exportDataframes(folder='./Mission_output/')




"""
Additional mission data processing

The flight optimization in [1] is primarely based on a state vector (RSV) of 
the Artemis I mission obtained through JPL Horizons. The following lines perform
some comparisons of the achieved state vector at the time of RSV.

These results are used in [1] for the tables 11 and 12.

"""

# reference state vector as obtained from JPL horizons
RSV_JDTBD = 2459899.877083333 #  2022-Nov-16 09:03:00.0000 JD TBD
RSV = np.array([-1.014728828823219E+04,  # km
                1.031292451321488E+04,   # km
                7.066845003764039E+03,   # km
                -6.770889903404616E+00,  # km/s
                6.431448996486860E-01,   # km/s
                1.099986116709792E+00,]) # km/s

#RSV_Simulated = missionObject.eventsDF.loc[23,['x','y','z','vx','vy','vz']].to_numpy()
RSV_Simulated = np.array([-10128615.021821234, 10295475.460099723, 7060732.22322179,
                -6776.333162878591, 643.4306613050503, 1102.1265577144918])

# RSV position and velocity differences (in [m| and [m/s]])
RSVpos_delta = RSV_Simulated[:3] - RSV[:3]*1000 
RSVvel_delta = RSV_Simulated[3:] - RSV[3:]*1000

# norm of position and velocity differences
RSVpos_delta_norm = np.linalg.norm(RSVpos_delta)
RSVvel_delta_norm = np.linalg.norm(RSVvel_delta)

# norm of velocity vectors
RSVvel_norm = np.linalg.norm(RSV[3:]*1000)
RSV_Sim_vel_norm = np.linalg.norm(RSV_Simulated[3:])

# differences of norms of velocity vectors
RSVvel_norm_delta = RSV_Sim_vel_norm - RSVvel_norm

# normalized velocity vector of RSV (used later for along/cross position)
RSVvel_normalized = RSV[3:] / np.linalg.norm(RSV[3:] )

# calculate along-track difference
posdiff_alongtrack = RSVvel_normalized.dot(RSVpos_delta)
# calculate cross-track difference
posdiff_crosstrack = np.sqrt(RSVpos_delta_norm**2-posdiff_alongtrack**2)

# flown distance (from liftoff on)
flown_distane = np.sum(np.linalg.norm(missionObject.missionDF.iloc[12:,9:12].to_numpy()-missionObject.missionDF.iloc[11:-1,9:12].to_numpy(),axis=1))

# rel error wrt flown distance
rel_error_posdiff_wrt_flowndist = RSVpos_delta_norm / flown_distane * 100

# angle between velocity vectors
angle_vel_vec_rad = np.arccos(np.dot(RSV_Simulated[3:],RSV[3:]*1000)/(RSVvel_norm*RSV_Sim_vel_norm))
angle_vel_vec_deg = angle_vel_vec_rad * 180/np.pi


# display found values
print('Absolute difference in velocities: {} m/s'.format(np.round(RSVvel_norm_delta,3)))
print('Norm of delta-v: {} m/s'.format(np.round(RSVvel_delta_norm,3)))
print('Distance between positions: {} km'.format(np.round(RSVpos_delta_norm/1000,3)))
print('Pos. difference along track: {} km'.format(np.round(posdiff_alongtrack/1000,3)))
print('Pos. difference cross track: {} km'.format(np.round(posdiff_crosstrack/1000,3)))
print('Along track difference in time: {} s'.format(posdiff_alongtrack/RSV_Sim_vel_norm))
print('Pos. difference w.r.t. to propagated distance: {}%'.format(np.round(rel_error_posdiff_wrt_flowndist,3)))
print('Time difference w.r.t. to propagation duration: {}%'.format(np.round((posdiff_alongtrack/RSV_Sim_vel_norm)/8046.8*100,3)))


