# !/usr/bin/env python3
"""
NodeServer to extract weather data from a Meteobridge Weather device.  Designed around a DAVIS VP2+ weather station. May work
others, not tested.  At the moment, only DAVIS stations provide ET0 readings.

Based on MeteoBridge nodeserver (meteobridgepoly) authored by Bob Paauwe
Customized to use template queries from MeteoBridge by Gordon Larsen

Copyright 2021 Robert Paauwe and Gordon Larsen, MIT License
"""
import time

import udi_interface

import write_profile
import uom
import requests

from nodes import TemperatureNode as tn
from nodes import HumidityNode as hn
from nodes import PressNode as pn
from nodes import WindNode as wn
from nodes import PrecipNode as rn
from nodes import LightNode as ln

from constants import *

LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom

"""
polyinterface has a LOGGER that is created by default and logs to:
logs/debug.log
You can use LOGGER.info, LOGGER.warning, LOGGER.debug, LOGGER.error levels as needed.
"""


class Controller(udi_interface.Node):
    id = 'meteobridge'
    drivers = [
        {'driver': 'ST', 'value': 1, 'uom': 2},
        {'driver': 'GV0', 'value': 0, 'uom': 25},
        {'driver': 'GV1', 'value': 0, 'uom': 25},
        {'driver': 'GV2', 'value': 0, 'uom': 56},
        {'driver': 'GV3', 'value': 0, 'uom': 58},
    ]

    def __init__(self, polyglot, parent, address, name):
        super(Controller, self).__init__(polyglot, parent, address, name)
        self.discovery_done = False
        self.stopping = None
        self.hb = 0
        self.poly = polyglot
        self.name = name
        self.address = address
        self.primary = parent
        self.configured = False

        self.password = ""
        self.username = "meteobridge"

        self.Parameters = Custom(polyglot, 'customparams')
        self.Notices = Custom(polyglot, 'notices')

        # self.poly.subscribe(self.poly.CONFIG, self.configHandler)
        self.poly.subscribe(self.poly.CUSTOMPARAMS, self.parameterHandler)
        self.poly.subscribe(self.poly.START, self.start, address)
        self.poly.subscribe(self.poly.POLL, self.poll)
        # self.poly.subscribe(self.poly.CUSTOMDATA, address)
        self.poly.subscribe(self.poly.ADDNODEDONE, self.node_queue)
        self.poly.subscribe(self.poly.STOP, self.stop)

        self.temperature_list = {}
        self.humidity_list = {}
        self.pressure_list = {}
        self.wind_list = {}
        self.rain_list = {}
        self.light_list = {}
        self.lightning_list = {}
        self.myConfig = {}  # custom parameters
        self.units = 'metric'
        self.ip = ""
        self.n_queue = []
        self.driver_list = []

        self.last_wind_dir = ''
        self.lastgooddata = None

        self.poly.ready()
        self.poly.addNode(self)

    def node_queue(self, data):
        self.n_queue.append(data['address'])

    def wait_for_node_done(self):
        while len(self.n_queue) == 0:
            time.sleep(0.1)
        self.n_queue.pop()

    def start(self):
        LOGGER.info('Starting Meteobridge Node Server')
        self.poly.setCustomParamsDoc()
        LOGGER.debug(f'self.configured: {self.configured}, self.discovery.done {self.discovery_done}')
        while not self.configured:
            time.sleep(10)

        LOGGER.debug('Calling discovery from the start method')
        self.discover()
        LOGGER.debug(f'Discovery done: {self.discovery_done}')

        LOGGER.debug(f'Connecting to Meteobridge at: {self.ip}')
        data, result = self.stationdata(self.ip, self.username, self.password)

        while result != 200:
            LOGGER.info("Node server not configured yet")
            return

        self.set_drivers(data)

    def poll(self, polltype):
        if 'longPoll' in polltype:
            pass
        else:
            # read data
            LOGGER.debug(f'Configured: {self.configured}')
            while not self.configured:
                LOGGER.info("Node server not configured yet")
                return

            data, result = self.stationdata(self.ip, self.username, self.password)
            LOGGER.debug(f'return from getstationdata {data} result code {result}')
            while result != 200:
                # return if configuration is incomplete or incorrect
                return

            self.set_drivers(data)
            LOGGER.info("Updated data from Meteobridge")

    def set_drivers(self, data):
        try:
            # Temperature values
            node = tn.TemperatureNode(self.poly, self.address, 'temps', 'Temperatures', self.units)
            tn.TemperatureNode.set_Driver(node, uom.TEMP_DRVS['main'], float(data[0]), )
            tn.TemperatureNode.set_Driver(node, uom.TEMP_DRVS['tempmax'], float(data[1]), )
            tn.TemperatureNode.set_Driver(node, uom.TEMP_DRVS['tempmin'], float(data[2]), )
            tn.TemperatureNode.set_Driver(node, uom.TEMP_DRVS['dewpoint'], float(data[3]), )
            tn.TemperatureNode.set_Driver(node, uom.TEMP_DRVS['windchill'], float(data[4]), )

            # Precipitation values
            node = rn.PrecipNode(self.poly, self.address, 'precip', 'Precipitation', self.units)
            rn.PrecipNode.set_Driver(node, uom.RAIN_DRVS['rate'], float(data[18]), )
            rn.PrecipNode.set_Driver(node, uom.RAIN_DRVS['daily'], float(data[19]), )
            rn.PrecipNode.set_Driver(node, uom.RAIN_DRVS['24hour'], float(data[20]), )
            rn.PrecipNode.set_Driver(node, uom.RAIN_DRVS['yesterday'], float(data[21]), )
            rn.PrecipNode.set_Driver(node, uom.RAIN_DRVS['monthly'], float(data[22]), )
            rn.PrecipNode.set_Driver(node, uom.RAIN_DRVS['yearly'], float(data[23]), )

            # Humidity values
            node = hn.HumidityNode(self.poly, self.address, 'humid', 'Humidity', self.driver_list)
            hn.HumidityNode.set_Driver(node, uom.HUMD_DRVS['main'], float(data[5]), )
            hn.HumidityNode.set_Driver(node, uom.HUMD_DRVS['max'], float(data[6]), )
            hn.HumidityNode.set_Driver(node, uom.HUMD_DRVS['min'], float(data[7]), )

            # Wind values
            node = wn.WindNode(self.poly, self.address, 'winds', 'Wind', self.units)

            try:  # Meteobridge seems to sometimes return a nul string for wind0dir-act=endir
                # so we substitute the last good reading
                # self.wind_dir_cardinal = self.wind_card_dict[data[17]]
                wind_dir_cardinal = cardinal_wind_dir_map(data[17])
                self.last_wind_dir = wind_dir_cardinal

            except:
                wind_dir_cardinal = self.last_wind_dir
                LOGGER.info(
                    f"Cardinal wind direction substituted for last good reading: {self.last_wind_dir} ({data[17]})")

            LOGGER.debug(
                f"mbr wind: {float(data[14])}, gust: {float(data[15])}, dir: {data[16]}, wdc: {data[17]}, "
                f"wind_dir_cardinal: {wind_dir_cardinal}, last_wind_dir: {self.last_wind_dir}")

            wn.WindNode.set_Driver(node, uom.WIND_DRVS['windspeed'], float(data[14]), )
            wn.WindNode.set_Driver(node, uom.WIND_DRVS['winddir'], data[16], )
            wn.WindNode.set_Driver(node, uom.WIND_DRVS['gustspeed'], float(data[15]), )
            wn.WindNode.set_Driver(node, uom.WIND_DRVS['windspeed1'], float(data[14]), )
            wn.WindNode.set_Driver(node, uom.WIND_DRVS['gustspeed1'], float(data[15]), )
            wn.WindNode.set_Driver(node, uom.WIND_DRVS['winddircard'], wind_dir_cardinal, )

            # Light values
            node = ln.LightNode(self.poly, self.address, 'solar', 'Illumination', self.units)
            try:
                uv = float(data[12])
                uvpresent = True

            except:  # no uv sensor
                uv = 0
                uvpresent = False

            try:
                solarradiation = float(data[11])
                et0 = float(data[13])
                vp2plus = True

            except:  # catch case where solar data is not available
                vp2plus = False
                solarradiation = 0
                et0 = 0

            ln.LightNode.set_Driver(node, uom.LITE_DRVS['solar_radiation'], solarradiation, )
            if uvpresent:
                ln.LightNode.set_Driver(node, uom.LITE_DRVS['uv'], uv, )
            else:
                ln.LightNode.set_Driver(node, uom.LITE_DRVS['uv'], 0, )
            if vp2plus:
                et0_conv = et0
                if self.units == 'us':
                    et0_conv = round(et0 / 25.4, 3)

                ln.LightNode.set_Driver(node, uom.LITE_DRVS['evapotranspiration'], et0_conv, )
            else:
                ln.LightNode.set_Driver(node, uom.LITE_DRVS['evapotranspiration'], 0, )
                LOGGER.info("Evapotranspiration not available (Davis Vantage stations with Solar Sensor only)")

            # Barometric pressure values
            node = pn.PressureNode(self.poly, self.address, 'press', 'Barometric Pressure', self.units)
            pn.PressureNode.set_Driver(node, uom.PRES_DRVS['station'], float(data[8]), )
            pn.PressureNode.set_Driver(node, uom.PRES_DRVS['sealevel'], float(data[9]), )
            pn.PressureNode.set_Driver(node, uom.PRES_DRVS['trend'], float(
                data[10]) + 1, )  # Meteobridge reports -1, 0, +1 for trends,converted for ISY

            # Update controller drivers now

            self.setDriver('GV3', data[30])  # Last good data
            self.setDriver('GV0', int(float(data[26])))  # Console battery
            self.setDriver('GV1', int(float(data[27])))  # ISS battery
            # value 0 = Ok, 1 = Replace
            self.setDriver('GV2', data[28])

            LOGGER.debug(f"Timestamp: {int(float(data[28]))}, Last good data: {data[30]} second(s) ago")

        except ValueError as e:
            LOGGER.error("Error in assigning driver values from template: {}".format(e))

    def discover(self, *args, **kwargs):
        LOGGER.info("Creating nodes.")
        # Temperatures Node
        node = tn.TemperatureNode(self.poly, self.address, 'temps', 'Temperatures', self.units)
        self.poly.addNode(node)
        self.wait_for_node_done()

        # Humiditys Node
        node = hn.HumidityNode(self.poly, self.address, 'humid', 'Humidity', self.humidity_list)
        self.poly.addNode(node)
        self.wait_for_node_done()

        # Barometric Pressures Node
        node = pn.PressureNode(self.poly, self.address, 'press', 'Barometric Pressure', self.units)
        self.poly.addNode(node)
        self.wait_for_node_done()

        # Winds Node
        node = wn.WindNode(self.poly, self.address, 'winds', 'Wind', self.units)
        self.poly.addNode(node)
        self.wait_for_node_done()

        # Precipitation node
        node = rn.PrecipNode(self.poly, self.address, 'precip', 'Precipitation', self.units)
        self.poly.addNode(node)
        self.wait_for_node_done()

        # Illumination node
        node = ln.LightNode(self.poly, self.address, 'solar', 'Illumination', self.units)
        self.poly.addNode(node)

        self.wait_for_node_done()

        self.discovery_done = True
        LOGGER.debug("Finished discovery, node setup complete")

    def delete(self):
        self.stopping = True
        LOGGER.warning('Removing Meteobridge nodeserver.')

    def stop(self):
        LOGGER.warning('Meteobridge NodeServer stopped.')
        self.poly.stop()

    def parameterHandler(self, config):
        self.Parameters.load(config)
        LOGGER.debug(f'Parameters: {self.Parameters}')
        self.Notices.clear()
        ip_exists = False
        password_exists = False

        self.ip = self.Parameters['IPAddress']
        if self.units is not None:
            self.units = self.Parameters['Units'].lower()
        self.password = self.Parameters['Password']

        # Add notices about missing configuration
        if self.ip == "":
            self.Notices['ipaddr'] = "IP address or hostname of your MeteoBridge device is required."
        else:
            ip_exists = True

        if self.password == "":
            self.Notices['Password'] = 'Password for MeteoBridge must be set'
        else:
            password_exists = True

        if ip_exists and password_exists:
            self.Notices.clear()
            self.setup_nodedefs(self.units)
            LOGGER.info(f'Configuration complete!')
            self.configured = True

    def setup_nodedefs(self, units):
        # Configure the units for each node driver
        self.temperature_list['main'] = 'I_TEMP_F' if units == 'us' else 'I_TEMP_C'
        self.temperature_list['dewpoint'] = 'I_TEMP_F' if units == 'us' else 'I_TEMP_C'
        self.temperature_list['windchill'] = 'I_TEMP_F' if units == 'us' else 'I_TEMP_C'
        self.temperature_list['tempmax'] = 'I_TEMP_F' if units == 'us' else 'I_TEMP_C'
        self.temperature_list['tempmin'] = 'I_TEMP_F' if units == 'us' else 'I_TEMP_C'
        self.humidity_list['main'] = 'I_HUMIDITY'
        self.humidity_list['max'] = 'I_HUMIDITY'
        self.humidity_list['min'] = 'I_HUMIDITY'
        self.pressure_list['station'] = 'I_INHG' if units == 'us' else 'I_MB'
        self.pressure_list['sealevel'] = 'I_INHG' if units == 'us' else 'I_MB'
        self.pressure_list['trend'] = 'I_TREND'
        self.wind_list['windspeed'] = 'I_MPS' if units == 'metric' else 'I_MPH'
        self.wind_list['gustspeed'] = 'I_MPS' if units == 'metric' else 'I_MPH'
        self.wind_list['winddir'] = 'I_DEGREE'
        self.wind_list['winddircard'] = 'I_CARDINAL'
        if units == 'metric':
            self.wind_list['windspeed1'] = 'I_KPH'
            self.wind_list['gustspeed1'] = 'I_KPH'
        else:
            self.wind_list['windspeed1'] = 'I_MPH'
            self.wind_list['gustspeed1'] = 'I_MPH'
        self.rain_list['rate'] = 'I_MMHR' if units == 'metric' else 'I_INHR'
        self.rain_list['daily'] = 'I_MM' if units == 'metric' else 'I_INCHES'
        self.rain_list['24hour'] = 'I_MM' if units == 'metric' else 'I_INCHES'
        self.rain_list['yesterday'] = 'I_MM' if units == 'metric' else 'I_INCHES'
        self.rain_list['monthly'] = 'I_MM' if units == 'metric' else 'I_INCHES'
        self.rain_list['yearly'] = 'I_MM' if units == 'metric' else 'I_INCHES'
        self.light_list['uv'] = 'I_UV'
        self.light_list['solar_radiation'] = 'I_RADIATION'
        self.light_list['evapotranspiration'] = 'I_MM' if units == 'metric' else 'I_INCHES'

        # Build the node definition
        LOGGER.info('Creating node definition profile based on config.')
        write_profile.write_profile(LOGGER, self.temperature_list,
                                    self.humidity_list, self.pressure_list, self.wind_list,
                                    self.rain_list, self.light_list, self.lightning_list)
        time.sleep(3)
        # push updated profile to ISY
        try:
            self.poly.updateProfile()

        except:
            LOGGER.error('Failed to push profile to ISY')

    def SetUnits(self, u):
        self.units = u

    # Hub status information here: battery and data health values.

    def stationdata(self, ipaddr, username, password):
        """
            Here we assemble the url and template for the call to the Meteobridge
            and then unpack the returned data into variables. Simplified in Version 1.2.5 to
            streamline the basic auth method in requests.get
        """
        try:

            values = str(mbtemplate())
            url = 'http://' + ipaddr + '/cgi-bin/template.cgi?template='
            LOGGER.debug("url in getstationdata: {}".format(url + values))

            u = requests.get(url + values, auth=(username, password))
            mbrdata = u.content.decode('utf-8')
            result_code = u.status_code
            LOGGER.debug(f'mbrdata is: {mbrdata}, status: {result_code}')
            if result_code != 200:
                LOGGER.error(f'Unable to connect to your Meteobridge device: {result_code}')
                return '', result_code

        except OSError as err:
            LOGGER.error(f"Unable to connect to your Meteobridge device: {err}")
            return

        mbrarray = mbrdata.split(" ")
        LOGGER.debug("mbrarray: {}".format(mbrarray))

        try:
            temperature = float(mbrarray[0])  # test that there's a valid response

        except ValueError or AttributeError as e:
            LOGGER.error(f"Error in getstationdata: {e}")
            LOGGER.error("Invalid value")
            LOGGER.error(mbrarray)

        return mbrarray, result_code
