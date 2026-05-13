# -*- coding: utf-8 -*-
"""
Created on Thu Apr 23 11:06:58 2026

@author: rappe
"""

#%%
from load_flow_config import load_flow_config
from create_flow_model import create_flow_model
from create_transport_model import create_transport_model
from plot_outputs import *
from utils import timeIndexForMaxConc, getConcMatrix, getTimes, getPointConc

import os
import flopy.utils.binaryfile as bf
import matplotlib.pyplot as plt
import numpy as np
import flopy

param_dic = load_flow_config()
print("Config loaded successfully")

Lx = param_dic["Lx"]
Ly = param_dic["Ly"]
c0 = param_dic["c0"]
source_row = param_dic["source_row"]
source_col = param_dic["source_col"]
obs_row, obs_col = param_dic["obs_row"], param_dic["obs_col"]
delr = param_dic["delr"]
ks = param_dic["hk"]
Lx = param_dic["Lx"]
prsity = param_dic["prsity"]

model_ws ="./model_no_sorption"
modelname_mf= "flow_model"
modelname_mt = 'transport_no_sorption'

mf, success, buff = create_flow_model(
    modelname_mf=modelname_mf,
    model_ws=model_ws,
    param_dic=param_dic
)
#%%
print(f"Flow model creation completed. Success: {success}")
if success:
    plot_head(model_ws, modelname_mf, Lx, Ly, nlayer=0)
    plot_head(model_ws, modelname_mf, Lx, Ly, nlayer=1)
    plot_head(model_ws, modelname_mf, Lx, Ly, nlayer=2)
    plot_head(model_ws, modelname_mf, Lx, Ly, nlayer=3)
    plot_head(model_ws, modelname_mf, Lx, Ly, nlayer=4)
    plot_head(model_ws, modelname_mf, Lx, Ly, nlayer=5)
else:
    print("Model run failed. Check the MODFLOW executable path and try again.")
    print("Buff:", buff)

# #%%

# print("Running Transport model...")
# # ===== MODEL NAME =====
# mt, success_mt, buff_mt, spd = create_transport_model(
#     modelname_mt=modelname_mt,
#     model_ws=model_ws,
#     mf=mf,
#     param_dic=param_dic,
#     kd = 0.001, lambda1 = 0.0, isothm = 0, ireact = 0, igetsc = 0
# )

# print(f"Transport model creation completed. Success: {success}")
# if success:
#     plot_btc(model_ws, obs_row, obs_col,0)
#     plot_concPlume(model_ws, obs_row, obs_col, Lx, Ly, source_row, source_col, c0)
# else:
#     print("Model run failed. Check the MODFLOW executable path and try again.")
#     print("Buff:", buff)

# #%%
# # well locations [layer, row, col, pumping_rate]
# # [[3, 72, 54, 30], [3, 93, 37, 30], [3, 100, 47, 30]]
# obs_row = 72
# obs_col = 54
# plot_btc(model_ws, obs_row, obs_col,0)    
# plot_btc(model_ws, obs_row, obs_col,1)
# plot_btc(model_ws, obs_row, obs_col,2)
# plot_btc(model_ws, obs_row, obs_col,3)
# plot_btc(model_ws, obs_row, obs_col,4)
# plot_btc(model_ws, obs_row, obs_col,5)
# #%%
# time_plot = 20
# plot_conc(model_ws, obs_row, obs_col, Lx, Ly, c0=1, nlayer=0, itime=time_plot)
# plot_conc(model_ws, obs_row, obs_col, Lx, Ly, c0=1, nlayer=1, itime=time_plot)
# plot_conc(model_ws, obs_row, obs_col, Lx, Ly, c0=1, nlayer=2, itime=time_plot)
# plot_conc(model_ws, obs_row, obs_col, Lx, Ly, c0=1, nlayer=3, itime=time_plot)
# plot_conc(model_ws, obs_row, obs_col, Lx, Ly, c0=1, nlayer=4, itime=time_plot)
# plot_conc(model_ws, obs_row, obs_col, Lx, Ly, c0=1, nlayer=5, itime=time_plot)





# %%
