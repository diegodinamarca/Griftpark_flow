  # -*- coding: utf-8 -*-
"""
Created on Thu Apr 23 11:05:39 2026

@author: rappe
"""

import numpy as np
import os
from load_head_file import *
from load_walls import *

def load_flow_config():

    # ===== PATHS =====
    exe_name_mf = r'C:\Simcore\PM8\modflow2005\mf2005'
    exe_name_mt = r'C:\Simcore\PM8\mt3dms\mt3dms5b'


    # head file
    headfile_L1 = "C:/Users/rappe/OneDrive/Documentos/Master Courses/EnvH/Griftpark/head_L1.tif"
    headfile_L2 = "C:/Users/rappe/OneDrive/Documentos/Master Courses/EnvH/Griftpark/head_L2.tif"
    headfiles = [headfile_L1, headfile_L2]
    
    # walls files
    walls_file = "C:/Users/rappe/OneDrive/Documentos/Master Courses/EnvH/Griftpark/cement_walls.tif"
    # ===== SPATIAL DISCRETIZATION =====
    # Lx = 400.0
    # Ly = 700.0

    ztop = 0.0
    zbot = [-5, -15, -35, -55.0, -60.0, -100.0]

    nlay = 6 # LAYER 1-4 (first acquitard) LAYER 5 = confining clay layer LAYER 6 = 2nd acquitard
    # nrow = 70
    # ncol = 40

    # delr = Lx / ncol
    # delc = Ly / nrow
    
    # ===== INITIAL HEAD =====
    # strt = np.ones((nlay, nrow, ncol), dtype=np.float32) * 25.0
    # strt[:, :, 0] = 25.0
    # strt[:, :, -1] = 24.5
    # strt = data
    # Load head field
    delc, delr, ncol, nrow, Lx, Ly, left, bottom, right, top = get_common_extent(headfiles)  # to verify common extent and cell sizes
    data = get_clipped_head_data(headfiles)  # to get head data clipped to common extent
    hdata = data[0]  # Assuming headfile_L1 corresponds to the first layer (L1)
    strt = list(nlay * [np.zeros((nrow, ncol), dtype=np.float32)])
    strt[0] = hdata
    strt[1] = hdata
    strt[2] = hdata
    strt[3] = hdata
    strt[4] = hdata
    hdata = data[1]  # Assuming headfile_L2 corresponds to the second layer (L2)
    strt[5] = hdata
    

    # ===== BOUNDARY CONDITIONS =====
    ibound = np.ones((nlay, nrow, ncol), dtype=np.int32)
    ibound[:, :, 0] = -1
    ibound[:, :, -1] = -1
    ibound[:, 0, :] = -1
    ibound[:, -1, :] = -1
    
    # ADD NOflow boundaries for cement walls
    # load cement walls
    walls = load_cementwalls(walls_file, left, bottom, right, top)    

    # ===== HYDRAULIC PARAMETERS =====
    # ===== FIRST FOR DIFFERENT LAYERS ===== --> BASED ON 1990 ARTICLE
    # hkLayer1 = 50 # 2500m^2 mentioned divided by layer thickness
    # hkLayer2 = 0.01 # 1990 article says between 0.25 and 0.01
    # hkLayer3 = 50 # 2000m^2 mentioned divided by layer thickness
    # hk = [20, 20, 80, 40, hkLayer2, hkLayer3]

    # list of K values, one per layer (length must equal nlay)
    k_values = np.array([20, 20, 80, 40, 0.01, 50], dtype=float)
    
    # hk has shape (nlay, nrow, ncol)
    hk = np.ones((nlay, nrow, ncol), dtype=float) * k_values[:, None, None]
    
    # set low conductivity in first 4 layers where walls == 1
    hk[:4, walls == 1] = 0.01
    
    # Assume vertical conductivity equal to horizontal
    vka = hk # ALSO ASSUMPTION
    ss = 0.0001
    laytyp = [1, 1, 1, 1, 0, 0] # 0=confined 1=unconfined

    # ===== TRANSPORT PARAMS (MT3DMS) =====
    prsity = 0.3
    
    # ===== RECHARGE ====== #
    rech = 0.0025 # m/d Based on KNMI data from 2018-2025 at the bilt

    # ===== TIME DISCRETIZATION =====
    nper_mf = 2
    nper_mt = 2
    perlen_mf = [11000, 35000]
    # perlen_mf = [110]*100+[350]*100

    perlen_mt = [11000, 35000]
    # perlen_mt = [110]*100+[350]*100
    nstp_mf = [200, 100]
    # nstp_mf = [20]*100+[10]*100

    nstp_mt = [200, 100]
    # nstp_mt = [20]*100+[10]*100

    steady_mf = [True, True]
    # steady_mf = [True]*nper_mf

    
    # ===== DISPERSION =====
    al = 3.0
    trpt = 0.3
    trpv = 0.3

    # ===== CONCENTRATION =====
    c0 = 1.0          # source concentration
    sconc = 0.0       # initial concentration
    active_periods = [c0, 0.0]
    # active_periods = [c0]*100+[0.0]*100

    # ===== ARRAYS =====
    icbund = np.ones((nlay, nrow, ncol), dtype=np.int32)
    sconc_array = np.full((nlay, nrow, ncol), sconc, dtype=np.float32)

    # ===== OBSERVATION POINT =====
    obs_row = 25
    obs_col = 50

    # ===== SOURCE LOCATION =====
    source_row = 25
    source_col = 0

    # ===== SORPTION / REACTION =====
    rhob = 2000.0
    kd = 0.000045
    lambda1 = 0.0

    isothm = 0
    ireact = 0
    igetsc = 0
    # ===== FINAL DICTIONARY =====
    param_dic = {

        # --- executables ---
        "exe_name_mf": exe_name_mf,
        "exe_name_mt": exe_name_mt,
        
        # --- input files ---
        "headfile_L1": headfile_L1,

        # --- grid ---
        "nlay": nlay,
        "nrow": nrow,
        "ncol": ncol,
        "delr": delr,
        "delc": delc,
        "ztop": ztop,
        "zbot": zbot,

        # --- time ---
        "nper_mf": nper_mf,
        "nper_mt": nper_mt,
        "perlen_mf": perlen_mf,
        "perlen_mt": perlen_mt,
        "nstp_mf": nstp_mf,
        "nstp_mt": nstp_mt,
        "steady_mf": steady_mf,

        # --- boundary & initial ---
        "ibound": ibound,
        "strt": strt,
        # --- hydraulic ---
        "laytyp": laytyp,
        "hk": hk,
        "vka": vka,
        "ss": ss,

        # --- transport ---
        "prsity": prsity,
        
        # --- recharge ---
        "rech" : rech,

        # --- optional ---
        "ipakcb": 53,
        "output_file_name": "mt3d_link.ftl",
        "compact_oc": True,
        "silent": True,
        "report": True,

        # --- metadata (no usado directamente por flopy pero útil) ---
        "Lx": Lx,
        "Ly": Ly,

        # --- basic transport ---
        "icbund": icbund,
        "sconc_array": sconc_array,

        # --- dispersion ---
        "al": al,
        "trpt": trpt,
        "trpv": trpv,

        # --- source ---
        "c0": c0,
        "source_row": source_row,
        "source_col": source_col,

        # --- observation ---
        "obs_row": obs_row,
        "obs_col": obs_col,

        # --- reaction / sorption ---
        "rhob": rhob,
        "kd": kd,
        "lambda1": lambda1,
        "isothm": isothm,
        "ireact": ireact,
        "igetsc": igetsc,

        # --- optional / defaults ---
        "ncomp": 1,
        "mixelm": 0,
        "percel": 0.75,
        "source_itype": 1,

        # source active first period only (default behavior)
        "source_active_periods": active_periods

    }

    return param_dic