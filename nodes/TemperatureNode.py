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
        self.node_drivers = Custom(polyglot, 'driverlist')

        # subscribe to the events we want
        self.poly.subscribe(polyglot.CUSTOMPARAMS, self.parameterHandler)
        self.poly.subscribe(self.poly.START, self.start, address)
        self.poly.subscribe(self.poly.CUSTOMNS, self.getnode_drivers)
        LOGGER.debug("Finished TemperatureNode __init__, drivers are: {}".format(self.drivers))

    def parameterHandler(self, params):
        self.Parameters.load(params)
        self.units = self.Parameters['Units']

    def getnode_drivers(self, driverdata):
        LOGGER.debug("Drivers are: {}".format(driverdata))

        self.drivers = self.node_drivers.load(driverdata)
        LOGGER.debug("Drivers are: {}".format(self.drivers))
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

    def start(self):
        nodes = self.poly.getNode('GV0')
        LOGGER.info("Found node {} ".format(nodes))

    def set_Driver(self, driver, value, **kwargs):
        if self.units == "us":
            value = (value * 1.8) + 32  # convert to F

        LOGGER.debug("In TempNode.setDriver: {} {}".format(driver, value))
        LOGGER.debug("Driver : {}".format(self.getDriver(driver)))
        # self.setDriver(driver, value)
        super(TemperatureNode, self).setDriver(driver, round(value, 1), report=True, force=True)
