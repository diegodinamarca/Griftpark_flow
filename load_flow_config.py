# -*- coding: utf-8 -*-
"""
Created on Thu Apr 23 11:05:39 2026

@author: rappe
"""

import numpy as np
import os

def load_flow_config():

    # ===== PATHS =====
    exe_name_mf = r'C:\Simcore\PM8\modflow2005\mf2005'
    exe_name_mt = r'C:\Simcore\PM8\mt3dms\mt3dms5b'

    # ===== SPATIAL DISCRETIZATION =====
    Lx = 1000.0
    Ly = 500.0

    ztop = 20.0
    zbot = 0.0

    nlay = 1
    nrow = 50
    ncol = 100

    delr = Lx / ncol
    delc = Ly / nrow

    # ===== BOUNDARY CONDITIONS =====
    ibound = np.ones((nlay, nrow, ncol), dtype=np.int32)
    ibound[:, :, 0] = -1
    ibound[:, :, -1] = -1

    # ===== INITIAL HEAD =====
    strt = np.ones((nlay, nrow, ncol), dtype=np.float32) * 25.0
    strt[:, :, 0] = 25.0
    strt[:, :, -1] = 24.5
    head_dif = 25.0 - 24.5
    # ===== HYDRAULIC PARAMETERS =====
    hk = 30.0
    vka = 30.0
    ss = 0.0001
    laytyp = 0

    # ===== TRANSPORT PARAMS (MT3DMS) =====
    prsity = 0.3

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

        # --- optional ---
        "ipakcb": 53,
        "output_file_name": "mt3d_link.ftl",
        "compact_oc": True,
        "silent": True,
        "report": True,

        # --- metadata (no usado directamente por flopy pero útil) ---
        "Lx": Lx,
        "Ly": Ly,
        "head_dif": head_dif,
        
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