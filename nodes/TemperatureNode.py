# !/usr/bin/env python3
"""
Polyglot v3 node server for Meteobridge
Copyright (C) 2021 Gordon Larsen
"""
import udi_interface
import sys

LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom


class TemperatureNode(udi_interface.Node):
    id = 'temperature'
    units = 'metric'
    drivers = []
    hint = [1, 0x0b, 1, 0]

    def __init__(self, polyglot, parent, address, name):
        super(TemperatureNode, self).__init__(polyglot, parent, address, name)

        self.poly = polyglot
        self.count = 0

        self.Parameters = Custom(polyglot, 'customparams')

        # subscribe to the events we want
        polyglot.subscribe(polyglot.CUSTOMPARAMS, self.parameterHandler)
#        polyglot.subscribe(polyglot.POLL, self.poll)

    def parameterHandler(self, params):
        self.Parameters.load(params)
        self.units = self.Parameters['Units']
    """
    def poll(self, polltype):

        if 'shortPoll' in polltype:
            if self.Parameters['multiplier'] is not None:
                mult = int(self.Parameters['multiplier'])
            else:
                mult = 1

            self.count += 1

            self.setDriver('GV0', self.count, True, True)
            self.setDriver('GV1', (self.count * mult), True, True)
    """

    def set_Driver(self, driver, value, **kwargs):
        if self.units == "us":
            value = (value * 1.8) + 32  # convert to F
        LOGGER.debug("In TempNode.setDriver: {} {}".format(driver, value))
        LOGGER.debug("Driver 'ST': {}".format(self.getDriver('ST')))
        self.setDriver(driver, value)
        # super(TemperatureNode, self).setDriver(driver, round(value, 1), report=True, force=True)
