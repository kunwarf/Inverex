#!/usr/bin/env python3
"""Run the addon."""

import logging
import sys
from math import modf
from pathlib import Path
from typing import Any, Callable, Dict, List, Sequence, Tuple
import time
import yaml
from filter import RROBIN, Filter, getfilter, suggested_filter
from mqtt import (
    MQTT,
    Device,
    Entity,
    NumberEntity,
    SelectEntity,
    SensorEntity,
    hass_default_rw_icon,
    hass_device_class,
)
from options import OPT, SS_TOPIC
from profiles import profile_add_entities, profile_poll

from definitions_5kw import ALL_SENSORS

   # , DEPRECATED, RATED_POWER
from rwsensors import NumberRWSensor, RWSensor, SelectRWSensor, TimeRWSensor
from sunsynk import Sensor, Sunsynk

_LOGGER = logging.getLogger(__name__)


DEVICE: Device = None
HASS_DISCOVERY_INFO_UPDATE_QUEUE: Dict[str, Filter] = {}
HIDDEN_SENSOR_IDS: set[str] = set()
SENSORS: List[Filter] = []
SENSOR_WRITE_QUEUE: Dict[str, Tuple[Filter, Any]] = {}
#SERIAL = ALL_SENSORS["serial"]
STARTUP_SENSORS: List[Filter] = []
SUNSYNK: Sunsynk = None  # type: ignore


def publish_sensors(sensors: List[Filter], *, force: bool = False) -> None:
    """Publish sensors."""
    for fsen in sensors:
        res = fsen.sensor.value
        res = fsen.update(res)
        if not force and res is None:
            continue
        if isinstance(res, float):
            if modf(res)[0] == 0:
                res = int(res)
            else:
                res = f"{res:.2f}".rstrip("0")
        print(f"{SS_TOPIC}/{OPT.sunsynk_id}/{fsen.sensor.id}", payload=str(res))


def setup_driver() -> None:
    """Setup the correct driver."""
    # pylint: disable=import-outside-toplevel
    global SUNSYNK  # pylint: disable=global-statement
    if OPT.driver == "pymodbus":
        from pysunsynk import pySunsynk
        SUNSYNK = pySunsynk()
        if not OPT.port:
            OPT.port = OPT.device
    else:
        _LOGGER.critical("Invalid DRIVER: %s. Expected umodbus, pymodbus", OPT.driver)
        sys.exit(-1)

    SUNSYNK.port = OPT.port
    SUNSYNK.server_id = OPT.modbus_server_id
    SUNSYNK.timeout = OPT.timeout
    SUNSYNK.read_sensors_batch_size = OPT.read_sensors_batch_size


def startup() -> None:
    """Read the hassos configuration."""
    logging.basicConfig(
        format="%(asctime)s %(levelname)-7s %(message)s", level=logging.DEBUG
    )

    configf = Path(__file__).parent / "config.yaml"
    OPT.update(yaml.safe_load(configf.read_text()).get("options", {}))
   # OPT.mqtt_host = sys.argv[1]
    #OPT.mqtt_password = sys.argv[2]
    OPT.debug = 1
    setup_driver()

    if OPT.debug < 2:
        logging.basicConfig(
            format="%(asctime)s %(levelname)-7s %(message)s",
            level=logging.INFO,
            force=True,
        )

    setup_sensors()


def setup_sensors() -> None:
    for sen in ALL_SENSORS.values():
        SUNSYNK.state.values[sen] = sen.id


def log_bold(msg: str) -> None:
    """Log a message."""
    _LOGGER.info("#" * 60)
    _LOGGER.info(f"{msg:^60}".rstrip())
    _LOGGER.info("#" * 60)


READ_ERRORS = 0

def read_sensors(
    sensors, msg: str = "", retry_single: bool = False
) -> bool:
    """Read from the Modbus interface."""
    global READ_ERRORS  # pylint:disable=global-statement
    try:
        SUNSYNK.read_sensors(sensors)
        READ_ERRORS = 0
        return True
    except Exception as err:  # pylint:disable=broad-except
        _LOGGER.error("Read Error%s: %s", msg, err)
        READ_ERRORS += 1
        if READ_ERRORS > 3:
            raise Exception(f"Multiple Modbus read errors: {err}") from err
    if retry_single:
        _LOGGER.info("Retrying individual sensors: %s", [s.name for s in SENSORS])
        for sen in sensors:
            read_sensors([sen], msg=sen.name, retry_single=False)

    return False


TERM = (
    "This Add-On will terminate in 30 seconds, "
    "use the Supervisor Watchdog to restart automatically."
)


def main() -> None:  # noqa
    """Main async loop."""
    #loop.set_debug(OPT.debug > 0)

    try:
        SUNSYNK.connect()
    except Exception:
        log_bold(f"Could not connect to {SUNSYNK.port}")
        _LOGGER.critical(TERM)
        return

    _LOGGER.info(
        "Reading startup sensors %s", ", ".join([s.id for s in STARTUP_SENSORS])
    )
#    for sen in STARTUP_SENSORS:
 #      SUNSYNK.state.values[sen] = sen
  #  read_sensors(STARTUP_SENSORS)

    #read_sensors(SUNSYNK.state.values.keys())
    #log_bold(f"Inverter serial number '{SERIAL}'")

    #if OPT.sunsynk_id != SERIAL and not OPT.sunsynk_id.startswith("_"):
     #   log_bold("SUNSYNK_ID should be set to the serial number of your Inverter!")
      #  return

    # Read all & publish immediately
    #read_sensors([f.sensor for f in SENSORS], retry_single=True)
    #publish_sensors(SENSORS, force=True)
    """
    def write_sensors() -> set[str]:
        Flush any pending sensor writes.
    while SENSOR_WRITE_QUEUE:
        _, (filt, value) = SENSOR_WRITE_QUEUE.popitem()
        sensor: RWSensor = filt.sensor
        old_reg_value = sensor.reg_value
        if not sensor.update_reg_value(value):
            continue

        _LOGGER.info(
                "Writing sensor %s: %s=%s  [old %s]",
                sensor.name,
                sensor.id,
                sensor.reg_value,
                old_reg_value,
        )
        SUNSYNK.write_sensor(sensor)
        read_sensors([sensor], msg=sensor.name)
        publish_sensors([filt], force=True) """

    def poll_sensors() -> None:
        """Poll sensors."""
        fsensors = []
        # 1. collect sensors to read
        RROBIN.tick()
        if SUNSYNK.state.values.keys():
            # 2. read
            read_sensors(SUNSYNK.state.values.keys())
                # 3. decode & publish
            #publish_sensors(fsensors)

    while True:
        #write_sensors()

        polltask = poll_sensors()
        try:
            polltask
        except Exception as exc:
            _LOGGER.error("TimeOut %s", exc)
            continue
        except AttributeError:
            # The read failed. Exit and let the watchdog restart
            return
        if OPT.profiles:
            profile_poll(SUNSYNK)
        for sen in SUNSYNK.state.values.keys():
            print(sen.id +":" + str(SUNSYNK.state.values[sen]))
        time.sleep(2)

if __name__ == "__main__":
    startup()
    main()