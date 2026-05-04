# -*- coding: utf-8 -*-
"""
Created on Thu Apr 23 11:06:58 2026

@author: rappe
"""

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
Lx = param_dic["Lx"]
Ly = param_dic["Ly"]
c0 = param_dic["c0"]
source_row = param_dic["source_row"]
source_col = param_dic["source_col"]
obs_row, obs_col = param_dic["obs_row"], param_dic["obs_col"]
delr = param_dic["delr"]
ks = param_dic["hk"]
head_dif = param_dic["head_dif"]
Lx = param_dic["Lx"]
prsity = param_dic["prsity"]


#%%
model_ws ="./model_no_sorption"
modelname_mf= "flow_model"
modelname_mt = 'transport_no_sorption'

mf, success, buff = create_flow_model(
    modelname_mf=modelname_mf,
    model_ws=model_ws,
    param_dic=param_dic
)

# ===== MODEL NAME =====
mt, success_mt, buff_mt, spd = create_transport_model(
    modelname_mt=modelname_mt,
    model_ws=model_ws,
    mf=mf,
    param_dic=param_dic,
    kd = 0.001, lambda1 = 0.0, isothm = 0, ireact = 0, igetsc = 0
)

plot_head(model_ws, modelname_mf, Lx, Ly)
plot_btc(model_ws, obs_row, obs_col)
plot_concPlume(model_ws, obs_row, obs_col, Lx, Ly, source_row, source_col, c0)

#%%
model_ws ="./model_eq_sorption"
modelname_mf= "flow_model"
modelname_mt = 'transport_eq_sorption'
    
mf, success, buff = create_flow_model(
    modelname_mf=modelname_mf,
    model_ws=model_ws,
    param_dic=param_dic
)
mt, success_mt, buff_mt, spd = create_transport_model(
    modelname_mt=modelname_mt,
    model_ws=model_ws,
    mf=mf,
    param_dic=param_dic,
    kd = 0.0001, alpha=0.3, lambda1 = 0.0, isothm = 1, ireact = 0, igetsc = 0
)
conc_nosorpt = getPointConc(model_ws, obs_row, obs_col)

plot_head(model_ws, modelname_mf, Lx, Ly)
plot_btc(model_ws, obs_row, obs_col)
plot_concPlume(model_ws, obs_row, obs_col, Lx, Ly, source_row, source_col, c0)

#%%
model_ws ="./model_kin_sorption"
modelname_mf= "flow_model"
modelname_mt = 'transport_kin_sorption'

mf, success, buff = create_flow_model(
    modelname_mf=modelname_mf,
    model_ws=model_ws,
    param_dic=param_dic
)

# ===== MODEL NAME =====
mt, success_mt, buff_mt, spd = create_transport_model(
    modelname_mt=modelname_mt,
    model_ws=model_ws,
    mf=mf,
    param_dic=param_dic,
    kd = 0.0001, alpha=0.0001, lambda1 = 0.0, isothm = 4, ireact = 0, igetsc = 0
)
plot_head(model_ws, modelname_mf, Lx, Ly)
plot_btc(model_ws, obs_row, obs_col)
plot_concPlume(model_ws, obs_row, obs_col, Lx, Ly, source_row, source_col, c0)

dist = (obs_col - source_col)*delr # distance traveled
q = head_dif/Lx # Darcy flow
v = q / prsity # flow velocity
alpha=0.0001
Da = alpha * dist / v #Damkohler number
#%%
plot_BTC_allmodels(obs_row, obs_col)
#%%

# =========== SENSITIVIY ANALYSIS FOR MASS TRANSFER =========
model_ws ="./model_kin_sorption"
modelname_mf= "flow_model"
modelname_mt = 'transport_kin_sorption'

mf, success, buff = create_flow_model(
    modelname_mf=modelname_mf,
    model_ws=model_ws,
    param_dic=param_dic
)

# ===== MODEL NAME =====
alpha_list = [0.1,0.01,0.001, 0.0001, 0.00001,0.000001]
import pandas as pd
times = getTimes(model_ws)
sens_data = pd.DataFrame({"time":times})
for a in alpha_list:
    mt, success_mt, buff_mt, spd = create_transport_model(
        modelname_mt=modelname_mt,
        model_ws=model_ws,
        mf=mf,
        param_dic=param_dic,
        kd = 0.0001, alpha=a, lambda1 = 0.0, isothm = 4, ireact = 0, igetsc = 0
    )
    conc = getPointConc(model_ws, obs_row, obs_col)
    sens_data[f"alpha_{a}"] = conc
    
dist = (obs_col - source_col)*delr # distance traveled
q = head_dif/Lx # Darcy flow
v = q / prsity # flow velocity
Da_list = np.array(alpha_list) * (dist / v) #Damkohler number
print(f'Damkohler Number for alpha={alpha_list} = {Da_list}')
#%%
# Plot BTC at observation point
fig, ax = plt.subplots(figsize=(10, 6))

ax.plot(sens_data["time"], sens_data["alpha_0.001"], linewidth=2, color = "blue", label = "0.001")
ax.plot(sens_data["time"], sens_data["alpha_0.0001"], linewidth=2, color = "green", label = "0.0001")
ax.plot(sens_data["time"], sens_data["alpha_1e-05"], linewidth=2, color = "gold", label = "0.00001")

ax.set_xlabel('Time (days)', fontsize=12)
ax.set_ylabel('Concentration', fontsize=12)
ax.set_title(f'Breakthrough Curve at Observation Point (x={obs_col*10}m, y={obs_row*10}m)', 
             fontsize=12)
ax.grid(True, alpha=0.3)
ax.set_xlim(0, times[-1])
ax.set_ylim(0, None)
ax.legend(title='Mass transfer parameter')
plt.tight_layout()
plt.savefig(f'breakthrough_curve_sensitivity_row{obs_row}_col{obs_col}.png', dpi=150)
plt.show()

#%%
# Plot BTC at observation point
fig, ax = plt.subplots(figsize=(10, 6))

ax.plot(sens_data["time"], sens_data["alpha_0.1"], linewidth=2, color = "blue", label = "0.1")
ax.plot(sens_data["time"], sens_data["alpha_0.01"], linewidth=2, color = "lightblue", label = "0.01")
ax.plot(sens_data["time"], sens_data["alpha_0.001"], linewidth=2, color = "purple", label = "0.001")
ax.plot(sens_data["time"], sens_data["alpha_0.0001"], linewidth=2, color = "green", label = "0.0001")
ax.plot(sens_data["time"], sens_data["alpha_1e-05"], linewidth=2, color = "gold", label = "0.00001")
ax.plot(sens_data["time"], sens_data["alpha_1e-06"], linewidth=2, color = "red", label = "0.000001")

ax.set_xlabel('Time (days)', fontsize=12)
ax.set_ylabel('Concentration', fontsize=12)
ax.set_title(f'Breakthrough Curve at Observation Point (x={obs_col*10}m, y={obs_row*10}m)', 
             fontsize=12)
ax.grid(True, alpha=0.3)
ax.set_xlim(0, times[-1])
ax.set_ylim(0, None)
ax.legend(title='Mass transfer parameter')
plt.tight_layout()
plt.savefig(f'breakthrough_curve_sensitivity_row{obs_row}_col{obs_col}.png', dpi=150)
plt.show()