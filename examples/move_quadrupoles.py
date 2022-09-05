import os.path
import xarray as xr
import pandas as pd
import numpy as np
from ophyd.status import AndStatus

from bact_dt.ophyd.devices.quadrupole import Quadrupole


quad_offsets = xr.open_dataarray(
    "/home/mfp/Devel/github/offsets_9ba454c7-f709-4c42-84b3-410b5ac05d9d.nc"
)

# print(quad_offsets)

prefix = "Pierre:DT"
for name in quad_offsets.coords["name"].values:
    name_lc = name.lower()
    dev = Quadrupole(prefix + ":" + name_lc, name=name_lc)
    vals = quad_offsets.sel(name=name)
    if not dev.connected:
        dev.wait_for_connection()
    stat_x = dev.x.set(vals.sel(plane="x", result="value"))
    stat_y = dev.y.set(vals.sel(plane="y", result="value"))
    AndStatus(stat_x, stat_y).wait(5.0)

    nx, ny = np.array([axis.readback.get() for axis in (dev.x, dev.y)]) * 1000
    print(f"{name}: moved to  {nx: 12.6f} {ny: 12.6f} mm")
    # break
