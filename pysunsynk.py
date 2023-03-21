"""Sunsync Modbus interface."""
import logging
from typing import Sequence
import attr
import serial
from sunsynk import Sunsynk  # type: ignore
import minimalmodbus
_LOGGER = logging.getLogger(__name__)

@attr.define
class pySunsynk(Sunsynk):  # pylint: disable=invalid-name
    """Sunsync Modbus class."""

    port: str = attr.ib(default="/dev/ttyUSB0")
    client: minimalmodbus.Instrument = attr.ib(default=None)

    def connect(self) -> None:
        """Connect"""
        client = None
        client = minimalmodbus.Instrument('/dev/ttyUSB0', 1)
        client.serial.baudrate = 9600  # Baud
        client.serial.bytesize = 8
        client.serial.parity = serial.PARITY_NONE
        client.serial.stopbits = 1
        client.mode = minimalmodbus.MODE_RTU  # rtu or ascii mode
        client.serial.timeout = 0.2
        self.client = client

    def write_register(self, *, address: int, value: int) -> bool:
        """Write to a register - Sunsynk supports modbus function 0x10."""
        try:
            self.client.write_registers(
                registeraddress=address, values=(value,))
            return True
        except Exception:
            _LOGGER.error("timeout writing register %s=%s", address, value)
        self.timeouts += 1
        return False

    def read_holding_registers(self, start: int, length: int) -> Sequence[int]:
        """Read a holding register."""
        try:
            res = self.client.read_registers(
                start, length, 3)
        except Exception:
            _LOGGER.error("timeout reading register %s=%s", start)
        self.timeouts += 1
        return res

