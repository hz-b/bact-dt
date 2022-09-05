from ophyd import (
    Component as Cpt,
    Device,
    EpicsSignal,
    EpicsSignalRO,
    Kind,
    PVPositionerPC,
)


class Parameters(Device):
    """Parameters of the model
    """

    hw2phys = Cpt(EpicsSignal, ":hw2phys", kind=Kind.config)


class KValue(Device):
    """Gradient / brho
    """

    setpoint = Cpt(EpicsSignalRO, ":set")
    readback = Cpt(EpicsSignalRO, ":rdbk")


class PowerConverter(Device):
    current = Cpt(EpicsSignal, ":I")
    muxer_current = Cpt(EpicsSignal, ":Imux")
    test_current = Cpt(EpicsSignal, ":dItest")


class Axis(PVPositionerPC):
    """A parameter of the axis
    """

    setpoint = Cpt(EpicsSignal, ":set")
    readback = Cpt(EpicsSignal, ":rdbk")


class InternalVariables(Device):
    Cm = Cpt(EpicsSignalRO, ":Cm")


class Quadrupole(Device):
    """One magnet
    """

    x = Cpt(Axis, ":x", name="x", egu="m")
    y = Cpt(Axis, ":y", name="y", egu="m")
    roll = Cpt(Axis, ":roll", name="roll")
    pc = Cpt(PowerConverter, ":im", name="pc")
    k = Cpt(KValue, ":Cm", name="k")
    par = Cpt(Parameters, ":par", name="par")
    im = Cpt(InternalVariables, ":im", name="im")


__all__ = ["Quadrupole", "Axis"]


def test_quadrupole():
    prefix = "Pierre:DT"
    quad = Quadrupole(prefix + ":q1m1d1r", name="q1")
    if not quad.connected:
        quad.wait_for_connection()

    hw2phys = quad.par.hw2phys.get()
    current = quad.pc.current.get()
    k = quad.k.setpoint.get()
    k_calc = current * hw2phys
    print(f"K set {k},  calc {k_calc} {current=} {hw2phys=}")


if __name__ == "__main__":
    test_quadrupole()
