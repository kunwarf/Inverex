"""Sunsynk 5kW&8kW hybrid inverter sensor definitions."""
from sunsynk import AMPS, CELSIUS, KWH, VOLT, WATT
from rwsensors import NumberRWSensor, SelectRWSensor, TimeRWSensor
from sensors import (
    FaultSensor,
    InverterStateSensor,
    MathSensor,
    SDStatusSensor,
    Sensor,
    SerialSensor,
    TempSensor,
)

_SENSORS: list[Sensor] = []
DEPRECATED: dict[str, Sensor] = {}

##########
# Battery
##########
_SENSORS += (
    TempSensor(182, "Battery temperature", CELSIUS, 0.1),
    Sensor(183, "Battery voltage", VOLT, 0.01),
    Sensor(184, "Battery SOC", "%"),
    Sensor(190, "Battery power", WATT, -1),
    Sensor(191, "Battery current", AMPS, -0.01),
)

#################
# Inverter Power
#################
_SENSORS += (
    Sensor(175, "Inverter power", WATT, -1),
    Sensor(154, "Inverter voltage", VOLT, 0.1),
    Sensor(193, "Inverter frequency", "Hz", 0.01),
)

#############
# Grid Power
#############
_SENSORS += (
    Sensor(79, "Grid frequency", "Hz", 0.01),
    Sensor(169, "Grid power", WATT, -1),  # L1(167) + L2(168)
    Sensor(167, "Grid LD power", WATT, -1),  # L1 seems to be LD
    Sensor(168, "Grid L2 power", WATT, -1),
    Sensor(150, "Grid voltage", VOLT, 0.1),
    MathSensor((160, 161), "Grid current", AMPS, factors=(0.01, 0.01)),
    Sensor(172, "Grid CT power", WATT, -1),
)

# LD power?

#############
# Load Power
#############
_SENSORS += (
    Sensor(178, "Load power", WATT, -1),  # L1(176) + L2(177)
    Sensor(176, "Load L1 power", WATT, -1),
    Sensor(177, "Load L2 power", WATT, -1),
)

################
# Solar Power 1
################
_SENSORS += (
    Sensor(186, "PV1 power", WATT, -1),
    Sensor(109, "PV1 voltage", VOLT, 0.1),
    Sensor(110, "PV1 current", AMPS, 0.1),
)

################
# Solar Power 2
################
_SENSORS += (
    Sensor(187, "PV2 power", WATT, -1),
    Sensor(111, "PV2 voltage", VOLT, 0.1),
    Sensor(112, "PV2 current", AMPS, 0.1),
)


###################
# Power on Outputs
###################
_SENSORS += (
    Sensor(166, "AUX power", WATT, -1),
    MathSensor(
        (175, 169, 166), "Essential power", WATT, factors=(1, 1, -1), absolute=True
    ),
    # MathSensor((175, 167, 166), "Essential power", WATT, factors=(1, 1, -1)),
    MathSensor(
        (172, 167), "Non-Essential power", WATT, factors=(1, -1), no_negative=True
    ),
)

###################
# Energy
###################
_SENSORS += (
    Sensor(60, "Day Active Energy", KWH, -0.1),
    Sensor(70, "Day Battery Charge", KWH, 0.1),
    Sensor(71, "Day Battery discharge", KWH, 0.1),
    Sensor(77, "Day Grid Export", KWH, 0.1),
    Sensor(76, "Day Grid Import", KWH, 0.1),
    # Sensor(200, "Day Load Power", KWH, 0.01),
    Sensor(84, "Day Load Energy", KWH, 0.1),
    Sensor(108, "Day PV Energy", KWH, 0.1),
    Sensor(61, "Day Reactive Energy", "kVarh", -0.1),
    # Sensor((201, 202), "History Load Power", KWH, 0.1),
    Sensor(67, "Month Grid Energy", KWH, 0.1),
    Sensor(66, "Month Load Energy", KWH, 0.1),
    Sensor(65, "Month PV Energy", KWH, 0.1),
    Sensor((63, 64), "Total Active Energy", KWH, 0.1),  # signed?
    Sensor((72, 73), "Total Battery Charge", KWH, 0.1),
    Sensor((74, 75), "Total Battery Discharge", KWH, 0.1),
    Sensor((81, 82), "Total Grid Export", KWH, 0.1),
    Sensor((78, 80), "Total Grid Import", KWH, 0.1),
    Sensor((85, 86), "Total Load Energy", KWH, 0.1),
    Sensor((96, 97), "Total PV Energy", KWH, 0.1),
    Sensor((98, 99), "Year Grid Export", KWH, 0.1),
    Sensor((87, 88), "Year Load Energy", KWH, 0.1),
    Sensor((68, 69), "Year PV Energy", KWH, 0.1),
)


##########
# General
##########
RATED_POWER = Sensor((16, 17), "Rated power", WATT, 0.1)
SERIAL = SerialSensor((3, 4, 5, 6, 7), "Serial")
_SENSORS.append(RATED_POWER)
_SENSORS += (
    RATED_POWER,
    SERIAL,
    Sensor(0, "Device Type"),
    FaultSensor((103, 104, 105, 106), "Fault"),
    InverterStateSensor(59, "Overall state"),
    SDStatusSensor(92, "SD Status", ""),  # type: ignore
    TempSensor(90, "DC transformer temperature", CELSIUS, 0.1),
    TempSensor(95, "Environment temperature", CELSIUS, 0.1),
    TempSensor(91, "Radiator temperature", CELSIUS, 0.1),
    Sensor(194, "Grid Connected Status"),
)

ALL_SENSORS: dict[str, Sensor] = {s.id: s for s in _SENSORS}
