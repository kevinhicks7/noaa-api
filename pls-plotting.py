import matplotlib.pyplot as plt
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
    aspect_ratio = models.AppBskyEmbedDefs.AspectRatio(height=1796, width=3169)
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
    fig = plt.figure(figsize=(12, 6))
    ax = plt.axes(projection=ccrs.LambertConformal())
    ax.set_extent([-120, -70, 25, 50], crs=ccrs.PlateCarree())
    anomaly.plot(
        ax=ax,
        transform=ccrs.PlateCarree(),
        cmap='RdBu_r',#'RdBu_r', 
        cbar_kwargs={'label': 'Max Temperature Anomaly (°C)'},
        vmin=-20, vmax=20
    )
    ax.add_feature(cfeature.OCEAN,facecolor='lightblue', alpha=1.0)
    ax.add_feature(cfeature.LAKES,facecolor='lightblue', alpha=1.0)
    ax.coastlines()
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.add_feature(cfeature.STATES, linewidth=0.5)

    ax.set_title(f'Max Temperature Anomaly\n{target_date} (°C)', fontsize=14)
    plt.tight_layout()
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