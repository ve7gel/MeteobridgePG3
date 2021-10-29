# !/usr/bin/env python3
"""
Polyglot v3 node server for Meteobridge
Copyright (C) 2021 Gordon Larsen
"""
import udi_interface
import uom

LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom


class PressureNode(udi_interface.Node):
    id = 'pressure'
    units = 'metric'
    drivers = []
    hint = [1, 0x0b, 1, 0]

    def __init__(self, polyglot, parent, address, name):
        super(PressureNode, self).__init__(polyglot, parent, address, name)

        self.poly = polyglot
        self.count = 0
        self.pressure_list = {}

        self.Parameters = Custom(polyglot, 'customparams')
        self.define_drivers()

        # subscribe to the events we want
        polyglot.subscribe(polyglot.CUSTOMPARAMS, self.parameterHandler)
#        polyglot.subscribe(polyglot.POLL, self.poll)

    def parameterHandler(self, params):
        self.Parameters.load(params)
        self.units = self.Parameters['Units']

    def set_Driver(self, driver, value, **kwargs):
        if self.units == "us":
            value = (value * 1.8) + 32  # convert to F

        super(PressureNode, self).setDriver(driver, round(value, 1), report=True, force=True)

    def define_drivers(self):
        # self.wait_for_node_done()
        self.pressure_list['station'] = 'I_INHG' if self.units == 'us' else 'I_MB'
        self.pressure_list['sealevel'] = 'I_INHG' if self.units == 'us' else 'I_MB'
        self.pressure_list['trend'] = 'I_TREND'
        driver_list = []

        for d in self.pressure_list:
            driver_list.append(
                {
                    'driver': uom.PRES_DRVS[d],
                    'value': 0,
                    'uom': uom.UOM[self.pressure_list[d]]
                })
        self.drivers = driver_list
        LOGGER.debug('Defining pressure drivers = {}'.format(self.drivers))

