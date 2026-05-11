# -*- coding: utf-8 -*-
"""
Created on Thu Apr 23 17:51:25 2026

@author: rappe
"""
import os
import flopy.utils.binaryfile as bf
import matplotlib.pyplot as plt
import numpy as np
import flopy
from utils import *
import pandas as pd

def plot_head(model_ws, modelname_mf, Lx, Ly, nlayer):
    # ===== READ AND PLOT HYDRAULIC HEAD =====
    # Read the head file
    headfile = os.path.join(model_ws, modelname_mf + '.hds')
    hds = bf.HeadFile(headfile)
    
    # Get head at the last time step
    times = hds.get_times()
    head = hds.get_data(totim=times[-1])
    
    # Create plot
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Define extent for proper axis labels
    extent = (0, Lx, 0, Ly)
    
    # Plot head distribution
    im = ax.imshow(head[nlayer], extent=extent, origin='lower', cmap='viridis')
    plt.colorbar(im, ax=ax, label='Hydraulic Head (m)')
    
    # Add contours
    levels = np.linspace(np.min(head[nlayer]), np.max(head[nlayer]), 15)
    cs = ax.contour(head[nlayer], levels=levels, extent=extent, colors='white', 
                    linewidths=0.5, origin='lower')
    ax.clabel(cs, fmt='%.2f', fontsize=8)
    
    ax.set_xlabel('x (m)')
    ax.set_ylabel('y (m)')
    ax.set_title(f'Hydraulic Head Distribution at t = {times[-1]:.0f} days')
    ax.set_aspect('equal')
    
    plt.tight_layout()
    plt.savefig(os.path.join(model_ws, f'head_distribution_layer{nlayer}.png'), dpi=150)
    plt.show()
    
    print(f"Head range: {np.min(head[0]):.2f} to {np.max(head[0]):.2f} m")
    
def plot_btc(model_ws, obs_row, obs_col, nlayer):
    ucnfile = os.path.join(model_ws, 'MT3D001.UCN')
    ucnobj = flopy.utils.UcnFile(ucnfile)
    
    # Get available times
    times_mt = ucnobj.get_times()
    
    print(f"Number of output times: {len(times_mt)}")
    print(f"Time range: {times_mt[0]:.1f} to {times_mt[-1]:.1f} days")
    
    # Get concentration at observation point for all times
    conc = ucnobj.get_alldata()
    print(conc.shape)
    conc_obs = conc[:, nlayer, obs_row, obs_col]
    
    ind = np.argmax(conc_obs)
    timeForMax = times_mt[ind]
    print(f"time for max concentration: at observation point {timeForMax:.0f}")
    print(f"maximum concentration at observation point: {conc_obs[ind]:.2f}")
    
    # Plot BTC at observation point
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.plot(times_mt, conc_obs, linewidth=2, color = "red", label = "No adsorption")
    ax.set_xlabel('Time (days)', fontsize=12)
    ax.set_ylabel('Concentration', fontsize=12)
    ax.set_title(f'Breakthrough Curve at Observation Point (x={obs_col*10}m, y={obs_row*10}m), layer={nlayer}', 
                 fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, times_mt[-1])
    ax.set_ylim(0, None)
    ax.legend(title='Concentration')
    plt.tight_layout()
    plt.savefig(os.path.join(model_ws, f'breakthrough_curve_row{obs_row}_col{obs_col}_layer{nlayer}.png'), dpi=150)
    plt.show()
    
    
def plot_concPlume(model_ws, obs_row, obs_col, Lx, Ly, source_row, source_col, c0):
    # Get concentration at final time
    time_plot = timeIndexForMaxConc(model_ws, obs_row, obs_col)
    times = getTimes(model_ws)
    conc = getConcMatrix(model_ws, timestp=time_plot)
    
    # Create plot
    fig, ax = plt.subplots(figsize=(10, 8))
    
    extent = (0, Lx/10, 0, Ly/10)
    
    # Plot concentration
    im = ax.imshow(conc[0], extent=extent, origin='lower', cmap='hot_r', 
                   vmin=0, vmax=c0)
    plt.colorbar(im, ax=ax, label='Concentration')
    
    # Add contours
    levels = [1, 5, 10, 20, 40, 60, 80]
    cs = ax.contour(conc[0], levels=levels, extent=extent, colors='black', 
                    linewidths=0.8, origin='lower')
    ax.clabel(cs, fmt='%.0f', fontsize=8)
    
    # Mark source location
    ax.plot(source_col, source_row, 'g*', markersize=15, label='Source')
    
    # Mark observation point
    ax.plot(obs_col, obs_row, 'bo', markersize=10, label='Observation')
    
    ax.set_xlabel('x (m)')
    ax.set_ylabel('y (m)')
    ax.set_title(f'Concentration Distribution at t = {times[time_plot]:.0f} days')
    ax.legend(loc='upper right')
    ax.set_aspect('equal')
    
    plt.tight_layout()
    plt.savefig(os.path.join(model_ws, 'concentration_final.png'), dpi=150)
    plt.show()
    
    print(f"Maximum concentration: {np.max(conc[0]):.2f}")
    print(f"Concentration at observation point: {conc[0, obs_row, obs_col]:.2f}")

def plot_conc(model_ws, obs_row, obs_col, Lx, Ly, c0, nlayer, time_plot):
    # Get concentration at final time
    # time_plot = timeIndexForMaxConc(model_ws, obs_row, obs_col)
    times = getTimes(model_ws)
    conc = getConcMatrix(model_ws, timestp=time_plot)
    
    # Create plot
    fig, ax = plt.subplots(figsize=(10, 8))
    
    extent = (0, Lx/10, 0, Ly/10)
    
    # Plot concentration
    im = ax.imshow(conc[nlayer], extent=extent, origin='lower', cmap='hot_r', 
                   vmin=0, vmax=c0)
    plt.colorbar(im, ax=ax, label='Concentration')
    
    # Add contours
    levels = [1, 5, 10, 20, 40, 60, 80]
    cs = ax.contour(conc[nlayer], levels=levels, extent=extent, colors='black', 
                    linewidths=0.8, origin='lower')
    ax.clabel(cs, fmt='%.0f', fontsize=8)
    
    # Mark observation point
    ax.plot(obs_col, obs_row, 'bo', markersize=10, label='Observation')
    
    ax.set_xlabel('x (m)')
    ax.set_ylabel('y (m)')
    ax.set_title(f'Concentration Distribution at t = {times[time_plot]:.0f} days, layer={nlayer}')
    ax.legend(loc='upper right')
    ax.set_aspect('equal')
    
    plt.tight_layout()
    plt.savefig(os.path.join(model_ws, f'concentration_final_layer{nlayer}.png'), dpi=150)
    plt.show()
    
    print(f"Maximum concentration: {np.max(conc[0]):.2f}")
    print(f"Concentration at observation point: {conc[nlayer, obs_row, obs_col]:.2f}")

def plot_BTC_allmodels(obs_row, obs_col):
    
    # BTC plotting of the three cases
    conc_nosorpt = getPointConc("./model_no_sorption", obs_row, obs_col)
    conc_eqsorpt = getPointConc("./model_eq_sorption", obs_row, obs_col)
    conc_kinsorpt = getPointConc("./model_kin_sorption", obs_row, obs_col)
    times = getTimes("./model_no_sorption")
    
    obs_nosorpt = pd.read_excel("Observed_conc_nosorpt.xlsx")
    obs_eqsorpt = pd.read_excel("Observed_conc_eqsorpt.xlsx")
    obs_kinsorpt = pd.read_excel("Observed_conc_kinsorpt.xlsx")
    
    
    # Plot BTC at observation point
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.plot(times, conc_nosorpt, linewidth=2, color = "blue", label = "No ads. Sim.")
    ax.plot(obs_nosorpt["time"], obs_nosorpt["conc"], linewidth=2, color = "blue", label = "No ads. Obs.", linestyle = "--")
    
    ax.plot(times, conc_eqsorpt, linewidth=2, color = "red", label = "Eq. ads. Sim.")
    ax.plot(obs_eqsorpt["time"], obs_eqsorpt["conc"], linewidth=2, color = "red", label = "Eq. ads. Obs.", linestyle = "--")
    
    ax.plot(times, conc_kinsorpt, linewidth=2, color = "gray", label = "Kin. ads. Sim.")
    ax.plot(obs_kinsorpt["time"], obs_kinsorpt["conc"], linewidth=2, color = "grey", label = "Kin. ads. Obs.", linestyle = "--")
    
    ax.set_xlabel('Time (days)', fontsize=12)
    ax.set_ylabel('Concentration', fontsize=12)
    ax.set_title(f'Breakthrough Curve at Observation Point (x={obs_col*10}m, y={obs_row*10}m)', 
                 fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, times[-1])
    ax.set_ylim(0, None)
    ax.legend(title='Concentration')
    plt.tight_layout()
    plt.savefig(f'breakthrough_curve_comparison_row{obs_row}_col{obs_col}.png', dpi=150)
    plt.show()