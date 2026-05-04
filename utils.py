# -*- coding: utf-8 -*-
"""
Created on Thu Apr 23 18:03:14 2026

@author: rappe
"""
import os
import flopy
import numpy as np
def timeIndexForMaxConc(model_ws, obs_row, obs_col):
    # ===== READ CONCENTRATION FILE =====
    ucnfile = os.path.join(model_ws, 'MT3D001.UCN')
    ucnobj = flopy.utils.UcnFile(ucnfile)
    # Get available times
    times_mt = ucnobj.get_times()
    # Get concentration at observation point for all times
    conc = ucnobj.get_alldata()
    conc_obs = conc[:, 0, obs_row, obs_col]
    ind = np.argmax(conc_obs)
    return(ind)

def getConcMatrix(model_ws, timestp):
    ucnfile = os.path.join(model_ws, 'MT3D001.UCN')
    ucnobj = flopy.utils.UcnFile(ucnfile)
    times_mt = ucnobj.get_times()
    conc = ucnobj.get_data(totim=times_mt[timestp])
    return conc


def getTimes(model_ws):
    ucnfile = os.path.join(model_ws, 'MT3D001.UCN')
    ucnobj = flopy.utils.UcnFile(ucnfile)
    # Get available times
    times_mt = ucnobj.get_times()
    return(times_mt)

def getPointConc(model_ws, obs_row, obs_col):
    ucnfile = os.path.join(model_ws, 'MT3D001.UCN')
    ucnobj = flopy.utils.UcnFile(ucnfile)
    
    # Get available times
    times_mt = ucnobj.get_times()
    
    print(f"Number of output times: {len(times_mt)}")
    print(f"Time range: {times_mt[0]:.1f} to {times_mt[-1]:.1f} days")
    
    # Get concentration at observation point for all times
    conc = ucnobj.get_alldata()
    conc_obs = conc[:, 0, obs_row, obs_col]
    return(conc_obs)