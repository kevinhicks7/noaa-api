import matplotlib.pyplot as plt
from matplotlib.colors import SymLogNorm
import matplotlib.colors as mcolors
import matplotlib.patheffects as path_effects
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import pandas as pd
import cfgrib
import xarray as xr
from datetime import datetime,timedelta
from atproto import Client, Request, models
import os

# https://csi.climatecentral.org/climate-shift-index?firstDate=2025-05-01&indicator=max&lat=43.98883&lng=-99.84026&mapType=anomalies&unit=F&zoom=4

def post(text,img):
    request = Request(timeout=None)  # Disable all timeouts by default.
    client = Client(request=request)
    pw = os.environ.get('BSKY_CLIMATE_BOT_PW') # from generated app password in bsky
    if pw is None:
        print('no bsky account password found')
        exit()
    client.login('us-climate-bot.bsky.social', pw)
    aspect_ratio = models.AppBskyEmbedDefs.AspectRatio(height=1748, width=2930)
    client.send_image(text=text, image=img, image_alt='Temperature map of U.S.',image_aspect_ratio=aspect_ratio,)

def get_data(target_date):
    year = pd.to_datetime(target_date).year
    dayofyear = pd.to_datetime(target_date).dayofyear

    # === URLs for NOAA CPC Global Unified Temperature (°C) ===
    # Daily max temp for the specific year
    daily_url = f"https://psl.noaa.gov/thredds/dodsC/Datasets/cpc_global_temp/tmax.{year}.nc"
    # Climatology from 1981–2010 (precomputed 365-day average)
    clim_url = "https://psl.noaa.gov/thredds/dodsC/Datasets/cpc_global_temp/tmax.day.ltm.1981-2010.nc"

    # === Load daily max temp for the day ===
    tmax_ds = xr.open_dataset(daily_url, engine='netcdf4')
    tmax_day = tmax_ds['tmax'].sel(time=target_date)

    # === Load climatology and match day ===
    time_coder = xr.coders.CFDatetimeCoder(use_cftime=True)
    clim_ds = xr.open_dataset(clim_url, engine='netcdf4', decode_times=time_coder)
    clim_day = clim_ds['tmax'].isel(time=dayofyear - 1)  # dayofyear is 1-based

    # === Compute anomaly (daily - climatology) ===
    anomaly = tmax_day - clim_day
    return anomaly


def plot(target_date,anomaly):
    top_cities = [
        {"name": "New York", "lat": 40.7128, "lon": -74.0060},
        {"name": "Los Angeles", "lat": 34.0522, "lon": -118.2437},
        {"name": "Chicago", "lat": 41.8781, "lon": -87.6298},
        {"name": "Houston", "lat": 29.7604, "lon": -95.3698},
        {"name": "Phoenix", "lat": 33.4484, "lon": -112.0740},
        {"name": "Philadelphia", "lat": 39.9526, "lon": -75.1652},
        {"name": "San Diego", "lat": 32.7157, "lon": -117.1611},
        {"name": "Dallas", "lat": 32.7767, "lon": -96.7970},
        {"name": "Austin", "lat": 30.2672, "lon": -97.7431},
        {"name": "Jacksonville", "lat": 30.3322, "lon": -81.6557},
        {"name": "Columbus", "lat": 39.9612, "lon": -82.9988},
        {"name": "San Francisco", "lat": 37.7749, "lon": -122.4194},
        {"name": "Charlotte", "lat": 35.2271, "lon": -80.8431},
        {"name": "Indianapolis", "lat": 39.7684, "lon": -86.1581},
        {"name": "Seattle", "lat": 47.6062, "lon": -122.3321},
        {"name": "Denver", "lat": 39.7392, "lon": -104.9903},
        {"name": "Washington", "lat": 38.9072, "lon": -77.0369},
        {"name": "Boston", "lat": 42.3601, "lon": -71.0589},
        {"name": "Nashville", "lat": 36.1627, "lon": -86.7816},
        {"name": "Detroit", "lat": 42.3314, "lon": -83.0458},
        {"name": "Memphis", "lat": 35.1495, "lon": -90.0490},
        {"name": "Portland", "lat": 45.5051, "lon": -122.6750},
        {"name": "Oklahoma City", "lat": 35.4676, "lon": -97.5164},
        {"name": "Las Vegas", "lat": 36.1699, "lon": -115.1398},
        {"name": "Milwaukee", "lat": 43.0389, "lon": -87.9065},
        {"name": "Albuquerque", "lat": 35.0844, "lon": -106.6504},
    ]

    fig = plt.figure(figsize=(12, 6))
    ax = plt.axes(projection=ccrs.LambertConformal())
    ax.set_extent([-120, -70, 25, 50], crs=ccrs.PlateCarree())

    bounds = [-24, -18, -12, -6, -3, -1, 0, 1, 3, 6, 12, 18, 24]
    cmap = plt.get_cmap('RdBu_r', len(bounds) + 1)
    norm = mcolors.BoundaryNorm(boundaries=bounds, ncolors=cmap.N, extend='both')

    contour = anomaly.plot(
        ax=ax,
        transform=ccrs.PlateCarree(),
        cmap=cmap,
        norm=norm,
        cbar_kwargs={
            'label': 'Max Temperature Anomaly (°C)',
            'ticks': bounds,
            'format': '%.0f',
            'extend': 'both'  
        }
    )
    cbar = ax.collections[0].colorbar
    cbar.ax.tick_params(labelsize=10)
    cbar.set_label('Max Temperature Anomaly (°C)', fontsize=12, labelpad=10)
    
    ax.add_feature(cfeature.OCEAN,facecolor='lightblue', alpha=1.0)
    ax.add_feature(cfeature.LAKES,facecolor='lightblue', alpha=1.0)
    ax.coastlines(linewidth=.5,color='gray')
    ax.add_feature(cfeature.BORDERS, linewidth=1.5,edgecolor='gray')
    ax.add_feature(cfeature.STATES, linewidth=0.5, edgecolor='gray')

    for city in top_cities:
        ax.plot(
            city['lon'], city['lat'],
            marker='o',
            color='gray',
            markersize=3,
            transform=ccrs.PlateCarree(),
            alpha=0.7
        )
        txt = ax.text(
            city['lon'] + 0.25,
            city['lat'] + 0.15,
            city['name'],
            transform=ccrs.PlateCarree(),
            fontsize=6,
            color='black',
            alpha=0.9,
            ha='left',
            va='bottom'
        )
        txt.set_path_effects([
            path_effects.Stroke(linewidth=1.5, foreground='white', alpha=0.8),
            path_effects.Normal()
        ])

    ax.text(-0.01, -0.05, 'Data: NOAA CPC  •  Map: @us-climate-bot.bsky.social', 
        transform=ax.transAxes, fontsize=9, color='gray', ha='left', va='top')

    ax.set_title(f'U.S. Temperature Difference from Normal:\n{target_date} (°C)', fontsize=14)
    plt.tight_layout(pad=2)

    #more formatting stuff for aesthetics
    plt.rcParams.update({
        'font.family': 'DejaVu Sans',
        'axes.titlesize': 18,
        'axes.labelsize': 12,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10
    })

    plt.savefig(f"tmax_anomaly", dpi=300, bbox_inches='tight')

    with open('tmax_anomaly.png', 'rb') as f:
        img_data = f.read()

    plt.close()
    return img_data

def main() -> None:
    yesterday = datetime.now() - timedelta(1)
    target_date = datetime.strftime(yesterday, '%Y-%m-%d')

    data = get_data(target_date)
    img_data = plot(target_date,data)
    post_text =f'U.S. Temperature Anomaly for {target_date}.'
    post(post_text,img_data)
    print('climate pls plotting ran')

if __name__ == '__main__':
    main()