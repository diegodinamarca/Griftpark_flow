# -*- coding: utf-8 -*-
"""
Created on Thu Apr 23 11:17:58 2026

@author: rappe
"""

import flopy
import numpy as np
def create_transport_model(modelname_mt, model_ws, mf, param_dic,
                           kd = 0.001, alpha = 1, lambda1 = 0.0, isothm = 0, ireact = 0, igetsc = 0):
    """
    Create an MT3DMS transport model linked to an existing MODFLOW model.

    Parameters
    ----------
    modelname_mt : str
        Name of the MT3DMS model.
    model_ws : str
        Workspace folder where MT3DMS files will be written.
    mf : flopy.modflow.Modflow
        Previously created MODFLOW model object.
    param_dic : dict
        Dictionary containing all required MT3DMS transport parameters.

    Required keys in param_dic
    --------------------------
    exe_name_mt : str
    icbund : array-like
    prsity : float or array-like
    sconc_array : array-like
    obs_row : int
    obs_col : int
    perlen_list : list
    nper : int
    al : float
    trpt : float
    trpv : float
    c0 : float
    source_row : int
    source_col : int
    isothm : int
    ireact : int
    igetsc : int
    rhob : float
    kd : float
    lambda1 : float

    Optional keys
    -------------
    ncomp : int, default 1
    mixelm : int, default 0
    percel : float, default 0.75
    source_itype : int, default 1
    source_active_periods : list, default first period on, rest off

    Returns
    -------
    mt : flopy.mt3d.Mt3dms
        Created MT3DMS model object.
    """

    # ---------- Required parameters ----------
    exe_name_mt = param_dic["exe_name_mt"]

    icbund = param_dic["icbund"]
    prsity = param_dic["prsity"]
    sconc_array = param_dic["sconc_array"]

    obs_row = param_dic["obs_row"]
    obs_col = param_dic["obs_col"]

    perlen_list = param_dic["perlen_mt"]
    nper = param_dic["nper_mt"]

    al = param_dic["al"]
    trpt = param_dic["trpt"]
    trpv = param_dic["trpv"]

    c0 = param_dic["c0"]
    source_row = param_dic["source_row"]
    source_col = param_dic["source_col"]

    rhob = param_dic["rhob"]

    # ---------- Optional parameters ----------
    ncomp = param_dic.get("ncomp", 1)
    mixelm = param_dic.get("mixelm", 0)
    percel = param_dic.get("percel", 0.75)
    source_itype = param_dic.get("source_itype", 1)
    silent = param_dic.get("silent", True)
    report = param_dic.get("report", True)
    # default behavior:
    # source active in first stress period, zero afterwards
    source_active_periods = param_dic.get(
        "source_active_periods",
        [c0] + [0.0] * (nper - 1)
    )

    # ---------- Basic validation ----------
    if len(perlen_list) != nper:
        raise ValueError(f"Length of perlen_list ({len(perlen_list)}) must equal nper ({nper}).")

    if len(source_active_periods) != nper:
        raise ValueError(
            f"Length of source_active_periods ({len(source_active_periods)}) must equal nper ({nper})."
        )

    # ===== CREATE MT3DMS MODEL =====
    mt = flopy.mt3d.Mt3dms(
        modelname=modelname_mt,
        model_ws=model_ws,
        exe_name=exe_name_mt,
        modflowmodel=mf
    )

    print(f"Created MT3DMS model: {modelname_mt}")
    print("Transport model is linked to flow model")
    timprs = np.linspace(0, 46000, 52)
    # ===== BASIC TRANSPORT PACKAGE =====
    btn = flopy.mt3d.Mt3dBtn(
        mt,
        icbund=icbund,
        prsity=prsity,
        sconc=sconc_array,
        ncomp=ncomp,
        obs=[(0, obs_row, obs_col)],
        perlen=perlen_list,
        nper=nper,
        # dt0=1.0,
        # mxstrn=100000,
        # ttsmult=1.0,
        timprs = timprs,
        nprs = len(timprs)
        # chkmas=True,
        # nprmas=1
    )

    print("BTN package created")
    print(f"Observation point at: row={obs_row}, col={obs_col}")

    # ===== ADVECTION PACKAGE =====
    adv = flopy.mt3d.Mt3dAdv(
        mt,
        mixelm=mixelm,
        percel=percel
    )

    print("ADV package created")

    # ===== DISPERSION PACKAGE =====
    dsp = flopy.mt3d.Mt3dDsp(
        mt,
        al=al,
        trpt=trpt,
        trpv=trpv
    )

    print("DSP package created")

    # ===== SOURCE/SINK MIXING PACKAGE =====
    spd = {}
    for kper in range(nper):
        spd[kper] = []
        for r in range(param_dic["nrow"]):
            spd[kper].append((0, r, 0, source_active_periods[kper], source_itype))
    ssm = flopy.mt3d.Mt3dSsm(
        mt,
        stress_period_data=spd
    )

    print("SSM package created")
    print(f"Contaminant source at: row={source_row}, col={source_col}")
    print(f"Initial source concentration: {c0}")

    # ===== SOLVER PACKAGE =====
    gcg = flopy.mt3d.Mt3dGcg(mt)

    print("GCG package created")

    # ===== REACTION / SORPTION PACKAGE =====
    rct = flopy.mt3d.Mt3dRct(
        mt,
        isothm=isothm,
        ireact=ireact,
        igetsc=igetsc,
        rhob=rhob,
        sp1=kd,
        sp2=alpha,
        rc1=lambda1,
        rc2=lambda1,
    )
    print("RCT package created")
    
    mt.write_input()
    print("MT3DMS input files written")
    
    # ===== RUN MT3DMS =====
    print("Running MT3DMS...")
    success_mt, buff_mt = mt.run_model(silent=silent, report=report)
    
    if success_mt:
        print("\n" + "="*50)
        print("MT3DMS completed successfully!")
        print("="*50)
    else:
        print("\nMT3DMS failed! Check the output for errors.")

    return mt, success_mt, buff_mt, spd