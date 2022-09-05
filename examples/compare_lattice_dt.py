"""Compare values of the quadrupoles to the ones in the lattice
"""
import os.path
import pandas as pd
import numpy as np
import thor_scsi.lib as ts_lib
from thor_scsi.factory import accelerator_from_config
from bact_dt.ophyd.devices.quadrupole import Quadrupole


t_dir = "/home/mfp/Devel/gitlab/dt4cc/"
# should not be here
lattice_dir = os.path.join(t_dir, "thor-scsi-lib/python/tests/lattices")
# should not be here
meas_dir = os.path.join(t_dir, "vaccelApp/Db/")

lat_file = os.path.join(lattice_dir, "b2_stduser_beamports_blm_tracy_corr.lat")
acc = accelerator_from_config(lat_file)

df = pd.read_json(os.path.join(meas_dir, "bessy2_quad_loco_current_hw2phys.json"))
# print(df)
# exit()

#
single_quad_to_pc = [
    name.replace("P", "M")
    for name in (
        "Q3P1T8R",
        "Q4P2T1R",
        "Q3P1T6R",
        "Q4P1T8R",
        "Q3P2T8R",
        "Q4P2T6R",
        "Q3P2T6R",
        "Q3P2T1R",
        "Q5P2T1R",
        "Q4P2T8R",
        "Q4P1T6R",
        "Q5P2T6R",
        "Q5P1T8R",
        "Q5P2T8R",
        "Q5P1T1R",
        "Q4P1T1R",
        "Q3P1T1R",
        "Q5P1T6R",
    )
]

prefix = "Pierre:DT"
for elem in acc:
    if isinstance(elem, ts_lib.Quadrupole):
        name = elem.name
        if name.upper() in single_quad_to_pc:
            # continue
            pass
        try:
            row = df.loc[name.upper(), :]
        except KeyError as ke:
            # QIT6L .. need to treat left and rigth
            print("No loco info on {name}")
            continue
        dev = Quadrupole(prefix + ":" + name, name=name)
        if not dev.connected:
            dev.wait_for_connection()
        # Trigger calculation propagation
        dev.pc.test_current.put(0.0)
        stat = dev.trigger()
        stat.wait(1)
        K_lat = elem.getMainMultipoleStrength().real
        K = row.val
        # print(dev.k.readback)
        K_dt = dev.k.readback.get()

        # K_dt = dev.im.Cm.get()
        K_rel = (1 - K / K_dt) * 1e4

        scale = 1000
        hw2phys_db = row.hw2phys_from_db * scale
        hw2phys = row.hw2phys * scale
        hw2phys_dt = dev.par.hw2phys.get() * scale
        hw2p_rel = (1 - hw2phys / hw2phys_dt) * 1e4

        eps = 1e-10
        if np.absolute(K_rel) > eps or np.absolute(hw2p_rel) > eps:
            txt = f"{name}: L {elem.getLength()*1000:8.3f}: K       lat {K_lat: 12.6f} loco {K: 12.6f} dt {K_dt: 12.6f}, rel {K_rel: 8.2f} units"
            print(txt)
            txt = f"{name}: L {elem.getLength()*1000:8.3f}: hw2phys db  {hw2phys_db: 12.6f} loco {hw2phys: 12.6f} dt {hw2phys_dt: 12.6f}, rel {hw2p_rel*2: 8.2f} units"
            print(txt)
