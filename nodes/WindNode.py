# !/usr/bin/env python3
"""
Polyglot v3 node server for Meteobridge
Copyright (C) 2021 Gordon Larsen
"""
import udi_interface
import uom

LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom


class WindNode(udi_interface.Node):
    id = 'wind'
    units = 'metric'
    drivers = []
    hint = [1, 0x0b, 1, 0]

    def __init__(self, polyglot, parent, address, name):
        super(WindNode, self).__init__(polyglot, parent, address, name)

        self.poly = polyglot
        self.count = 0
        self.wind_list = {}

        self.Parameters = Custom(polyglot, 'customparams')
        self.define_drivers()

        # subscribe to the events we want
        polyglot.subscribe(polyglot.CUSTOMPARAMS, self.parameterHandler)

    #        polyglot.subscribe(polyglot.POLL, self.poll)

    def parameterHandler(self, params):
        self.Parameters.load(params)
        self.units = self.Parameters['Units']

    def set_Driver(self, driver, value, **kwargs):
        LOGGER.debug("WindNode.set_Driver driver {} value {}".format(driver, value))
        if self.units == "us" and (driver == 'GV3' or driver == 'GV4'):
            value = (value * .8)  # convert to MPH

        super(WindNode, self).setDriver(driver, round(value, 1), report=True, force=True)

    def define_drivers(self):
        self.wind_list['windspeed'] = 'I_MPS' if self.units == 'metric' else 'I_MPH'
        self.wind_list['gustspeed'] = 'I_MPS' if self.units == 'metric' else 'I_MPH'
        self.wind_list['winddir'] = 'I_DEGREE'
        self.wind_list['winddircard'] = 'I_CARDINAL'
        if self.units == 'metric':
            self.wind_list['windspeed1'] = 'I_KPH'
            self.wind_list['gustspeed1'] = 'I_KPH'

        driver_list = []

        for d in self.wind_list:
            driver_list.append(
                {
                    'driver': uom.WIND_DRVS[d],
                    'value': 0,
                    'uom': uom.UOM[self.wind_list[d]]
                })
        self.drivers = driver_list
        LOGGER.debug('Defining wind drivers = {}'.format(self.drivers))
        # self.wait_for_node_done()
