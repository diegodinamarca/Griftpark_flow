# -*- coding: utf-8 -*-
"""
Created on Thu Apr 23 11:00:29 2026

@author: rappe
"""

import flopy
def create_flow_model(modelname_mf, model_ws, param_dic):
    """
    Create, write, and run a MODFLOW flow model using parameters
    provided in a dictionary loaded from an external config file.

    Parameters
    ----------
    modelname_mf : str
        Name of the MODFLOW model.
    model_ws : str
        Workspace folder where MODFLOW files will be written.
    param_dic : dict
        Dictionary containing all required model parameters.

    Required keys in param_dic
    --------------------------
    exe_name_mf : str
    nlay : int
    nrow : int
    ncol : int
    delr : float or array-like
    delc : float or array-like
    ztop : float or array-like
    zbot : float or array-like
    nper : int
    perlen_list : list
    nstp_list : list
    steady_list : list
    ibound : array-like
    strt : array-like
    laytyp : int or list
    hk : array-like
    vka : array-like
    ss : float or array-like

    Optional keys
    -------------
    ipakcb : int, default 53
    output_file_name : str, default 'mt3d_link.ftl'
    compact_oc : bool, default True
    silent : bool, default True
    report : bool, default True

    Returns
    -------
    mf : flopy.modflow.Modflow
        The created MODFLOW model object.
    success : bool
        Whether the model ran successfully.
    buff : list
        MODFLOW run output.
    """

    # ---------- Required parameters ----------
    exe_name_mf = param_dic["exe_name_mf"]

    nlay = param_dic["nlay"]
    nrow = param_dic["nrow"]
    ncol = param_dic["ncol"]

    delr = param_dic["delr"]
    delc = param_dic["delc"]
    ztop = param_dic["ztop"]
    zbot = param_dic["zbot"]

    nper = param_dic["nper_mf"]
    perlen_list = param_dic["perlen_mf"]
    nstp_list = param_dic["nstp_mf"]
    steady_list = param_dic["steady_mf"]

    ibound = param_dic["ibound"]
    strt = param_dic["strt"]

    laytyp = param_dic["laytyp"]
    hk = param_dic["hk"]
    vka = param_dic["vka"]
    ss = param_dic["ss"]
    rech = param_dic["rech"]

    # ---------- Optional parameters ----------
    ipakcb = param_dic.get("ipakcb", 53)
    output_file_name = param_dic.get("output_file_name", "mt3d_link.ftl")
    compact_oc = param_dic.get("compact_oc", True)
    silent = param_dic.get("silent", True)
    report = param_dic.get("report", True)

    # ---------- Basic validation ----------
    if nper > 1:
        if len(perlen_list) != nper:
            raise ValueError(f"Length of perlen_list ({len(perlen_list)}) must equal nper ({nper}).")

        if len(nstp_list) != nper:
            raise ValueError(f"Length of nstp_list ({len(nstp_list)}) must equal nper ({nper}).")
    
        if len(steady_list) != nper:
            raise ValueError(f"Length of steady_list ({len(steady_list)}) must equal nper ({nper}).")

    # ===== CREATE MODFLOW MODEL =====
    mf = flopy.modflow.Modflow(
        modelname=modelname_mf,
        exe_name=exe_name_mf,
        model_ws=model_ws
    )
    print(f"Created MODFLOW model: {modelname_mf}")
    # ===== DISCRETIZATION PACKAGE =====
    dis = flopy.modflow.ModflowDis(
        mf,
        nlay=nlay,
        nrow=nrow,
        ncol=ncol,
        delr=delr,
        delc=delc,
        top=ztop,
        botm=zbot,
        nper=nper,
        perlen=perlen_list,
        nstp=nstp_list,
        steady=steady_list
    )
    print("DIS package created")

    # ===== BASIC PACKAGE =====
    bas = flopy.modflow.ModflowBas(
        mf,
        ibound=ibound,
        strt=strt
    )
    print("BAS package created")

    # ===== LAYER PROPERTY FLOW PACKAGE =====
    lpf = flopy.modflow.ModflowLpf(
        mf,
        laytyp=laytyp,
        hk=hk,
        vka=vka,
        ipakcb=ipakcb,
        ss=ss
    )
    print("LPF package created")
    
    # ===== RECHARGE PACKAGE ====== #
    # rch = flopy.modflow.ModflowRch(mf, rech=rech)

    # ===== OUTPUT CONTROL PACKAGE =====
    stress_period_data = {}
    for kper in range(nper):
        for kstp in range(nstp_list[kper]):
            stress_period_data[(kper, kstp)] = ["save head", "save budget"]

    oc = flopy.modflow.ModflowOc(
        mf,
        stress_period_data=stress_period_data,
        compact=compact_oc
    )
    print("OC package created")

    # ===== SOLVER PACKAGE =====
    pcg = flopy.modflow.ModflowPcg(mf)
    print("PCG package created")

    # ===== LINK-MT3DMS PACKAGE =====
    lmt = flopy.modflow.ModflowLmt(
        mf,
        output_file_name=output_file_name
    )
    print("LMT package created - flow model is now linked to transport model")

    # ===== WRITE INPUT FILES =====
    mf.write_input()
    print("MODFLOW input files written to:", model_ws)

    # ===== RUN MODFLOW =====
    print("Running MODFLOW...")
    success, buff = mf.run_model(silent=silent, report=report)

    if success:
        print("\n" + "=" * 50)
        print("MODFLOW completed successfully!")
        print("=" * 50)
    else:
        print("\nMODFLOW failed! Check the listing file for errors.")

    return mf, success, buff