# !/usr/bin/env python3
"""
NodeServer to extract weather data from a Meteobridge Weather device.  Designed around a DAVIS VP2+ weather station. May work
others, not tested.  At the moment, only DAVIS stations provide ET0 readings.

Based on MeteoBridge nodeserver (meteobridgepoly) authored by Bob Paauwe
Customized to use template queries from MeteoBridge by Gordon Larsen

Copyright 2020 Robert Paauwe and Gordon Larsen, MIT License
"""
import time

import udi_interface

import sys
import write_profile
import uom
import requests
from nodes import TemperatureNode as tn
from nodes import HumidityNode as hn
from nodes import PressNode as pn
from nodes import WindNode as wn
from nodes import PrecipNode as rn
from nodes import LightNode as ln

LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom

"""
polyinterface has a LOGGER that is created by default and logs to:
logs/debug.log
You can use LOGGER.info, LOGGER.warning, LOGGER.debug, LOGGER.error levels as needed.
"""


class Controller(udi_interface.Node):
    id = 'MeteoBridge'

    def __init__(self, polyglot, parent, address, name):
        super(Controller, self).__init__(polyglot, parent, address, name)
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
        self.node_drivers = Custom(polyglot, 'customdata')

        # self.poly.subscribe(self.poly.CONFIG, self.configHandler)
        self.poly.subscribe(self.poly.CUSTOMPARAMS, self.parameterHandler)
        self.poly.subscribe(self.poly.START, self.start, address)
        self.poly.subscribe(self.poly.POLL, self.poll)
        # self.poly.subscribe(self.poly.CUSTOMNDATA, address)
        # self.poly.subscribe(self.poly.ADDNODEDONE, self.nodeHandler)

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

        self.wind_card_dict = {
            'N': 0,
            'NNE': 1,
            'NE': 2,
            'ENE': 3,
            'E': 4,
            'ESE': 5,
            'SE': 6,
            'SSE': 7,
            'S': 8,
            'SSW': 9,
            'SW': 10,
            'WSW': 11,
            'W': 12,
            'WNW': 13,
            'NW': 14,
            'NNW': 15
        }
        self.last_wind_dir = ''
        self.vp2plus = False
        self.uvpresent = False
        self.lastgooddata = None

        polyglot.ready()
        polyglot.addNode(self)

    def node_queue(self, data):
        self.n_queue.append(data['address'])

    def wait_for_node_done(self):
        while len(self.n_queue) == 0:
            time.sleep(0.1)
        self.n_queue.pop()

    def start(self):
        LOGGER.info('Started MeteoBridge Template NodeServer')

        if self.ip != "":
            self.discover()
            LOGGER.debug('Connecting to Meteobridge at: {}'.format(self.ip))
            self.getstationdata(self.ip, self.username, self.password)
            self.set_drivers()

    def poll(self, polltype):
        if 'longPoll' in polltype:
            pass
        else:
            # read data
            if self.ip == "":
                return

            self.getstationdata(self.ip, self.username, self.password)
            self.set_drivers()
            LOGGER.info("Updated data from Meteobridge")

    def set_drivers(self):
        try:
            node = tn.TemperatureNode(self.poly, self.address, 'temps', 'Temperatures')
            tn.TemperatureNode.set_Driver(node, uom.TEMP_DRVS['main'], self.temperature, )
            tn.TemperatureNode.set_Driver(node, uom.TEMP_DRVS['dewpoint'], self.dewpoint, )
            tn.TemperatureNode.set_Driver(node, uom.TEMP_DRVS['windchill'], self.windchill, )
            tn.TemperatureNode.set_Driver(node, uom.TEMP_DRVS['tempmax'], self.maxtemp, )
            tn.TemperatureNode.set_Driver(node, uom.TEMP_DRVS['tempmin'], self.mintemp, )

            node = rn.PrecipNode(self.poly, self.address, 'precip', 'Precipitation')
            rn.PrecipNode.set_Driver(node, uom.RAIN_DRVS['rate'], self.rain_rate, )
            rn.PrecipNode.set_Driver(node, uom.RAIN_DRVS['daily'], self.rain_today, )
            rn.PrecipNode.set_Driver(node, uom.RAIN_DRVS['24hour'], self.rain_24hour, )
            rn.PrecipNode.set_Driver(node, uom.RAIN_DRVS['yesterday'], self.rain_yesterday, )
            rn.PrecipNode.set_Driver(node, uom.RAIN_DRVS['monthly'], self.rain_month, )
            rn.PrecipNode.set_Driver(node, uom.RAIN_DRVS['yearly'], self.rain_year, )

            node = hn.HumidityNode(self.poly, self.address, 'humid', 'Humidity')
            hn.HumidityNode.set_Driver(node, uom.HUMD_DRVS['main'], self.rh, )

            '''
            self.poly.nodes['wind'].setDriver(uom.WIND_DRVS['windspeed'], self.wind, )
            self.poly.nodes['wind'].setDriver(uom.WIND_DRVS['winddir'], self.wind_dir, )
            self.poly.nodes['wind'].setDriver(uom.WIND_DRVS['gustspeed'], self.wind_gust, )
            self.poly.nodes['wind'].setDriver(uom.WIND_DRVS['windspeed1'], self.wind, )
            self.poly.nodes['wind'].setDriver(uom.WIND_DRVS['gustspeed1'], self.wind_gust, )
            self.poly.nodes['wind'].setDriver(uom.WIND_DRVS['winddircard'], self.wind_dir_cardinal, )
            self.poly.nodes['light'].setDriver(uom.LITE_DRVS['solar_radiation'], self.solarradiation, )
            if self.uvpresent:
                self.poly.nodes['light'].setDriver(uom.LITE_DRVS['uv'], self.uv, )
            else:
                self.poly.nodes['light'].setDriver(uom.LITE_DRVS['uv'], 0, )
            if self.vp2plus:
                et0_conv = self.et0
                if self.units == 'us':
                    et0_conv = round(et0_conv / 25.4, 3)

                self.poly.nodes['light'].setDriver(uom.LITE_DRVS['evapotranspiration'], et0_conv, )
            else:
                self.poly.nodes['light'].setDriver(uom.LITE_DRVS['evapotranspiration'], 0, )
                LOGGER.info("Evapotranspiration not available (Davis Vantage stations with Solar Sensor only)")
            '''
            node = pn.PressureNode(self.poly, self.address, 'humid', 'Humidity')

            pn.PressureNode.set_Driver(node, uom.PRES_DRVS['station'], self.stn_pressure, )
            pn.PressureNode.set_Driver(node, uom.PRES_DRVS['sealevel'], self.sl_pressure, )
            pn.PressureNode.set_Driver(node, uom.PRES_DRVS['trend'], self.pressure_trend, )

            # Update controller drivers now
            self.setDriver('GV3', self.lastgooddata)
            self.setDriver('GV0', self.battery)
            self.setDriver('GV1', self.issbattery)
            # value 0 = Ok, 1 = Replace
            self.setDriver('GV2', self.timestamp)

            LOGGER.debug("Last good data: {} second(s) ago".format(self.lastgooddata))

        except ValueError as e:
            LOGGER.error("Error in assigning driver values from template: {}".format(e))

    def query(self, command=None):
        for node in self.poly.nodes:
            self.poly.nodes[node].reportDrivers()

    def discover(self, *args, **kwargs):

        LOGGER.info("Creating nodes.")
        # Temperatures Node
        node = tn.TemperatureNode(self.poly, self.address, 'temps', 'Temperatures')
        self.poly.addNode(node)

        # Humidity Node
        node = hn.HumidityNode(self.poly, self.address, 'humid', 'Humidity')
        self.poly.addNode(node)

        # Barometric Pressures Node
        node = pn.PressureNode(self.poly, self.address, 'press', 'Barometric Pressure')
        self.poly.addNode(node)

        # Winds Node
        node = wn.WindNode(self.poly, self.address, 'winds', 'Wind')
        self.poly.addNode(node)

        # Precipitation node
        node = rn.PrecipNode(self.poly, self.address, 'precip', 'Precipitation')
        self.poly.addNode(node)

        # Illumination node
        node = ln.LightNode(self.poly, self.address, 'solar', 'Illumination')
        self.poly.addNode(node)

        self.wait_for_node_done()

    def delete(self):
        self.stopping = True
        LOGGER.info('Removing MeteoBridge Template nodeserver.')

    def stop(self):
        LOGGER.info('NodeServer stopped.')

    def parameterHandler(self, config):
        self.Parameters.load(config)
        self.Notices.clear()
        ip_exists = False
        password_exists = False

        self.ip = self.Parameters['IPAddress']
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

    def setup_nodedefs(self, units):
        # Configure the units for each node driver
        self.temperature_list['main'] = 'I_TEMP_F' if units == 'us' else 'I_TEMP_C'
        self.temperature_list['dewpoint'] = 'I_TEMP_F' if units == 'us' else 'I_TEMP_C'
        self.temperature_list['windchill'] = 'I_TEMP_F' if units == 'us' else 'I_TEMP_C'
        self.temperature_list['tempmax'] = 'I_TEMP_F' if units == 'us' else 'I_TEMP_C'
        self.temperature_list['tempmin'] = 'I_TEMP_F' if units == 'us' else 'I_TEMP_C'
        self.humidity_list['main'] = 'I_HUMIDITY'
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

    def update_profile(self, command):
        LOGGER.info('update_profile:')
        st = self.poly.updateProfile()
        return st

    def SetUnits(self, u):
        self.units = u

    commands = {
        'QUERY': query,
        'DISCOVER': discover,
        'UPDATE_PROFILE': update_profile,
    }
    # Hub status information here: battery and data health values.
    drivers = [
        {'driver': 'ST', 'value': 1, 'uom': 2},
        {'driver': 'GV0', 'value': 0, 'uom': 25},
        {'driver': 'GV1', 'value': 0, 'uom': 25},
        {'driver': 'GV2', 'value': 0, 'uom': 0},
        {'driver': 'GV3', 'value': 0, 'uom': 58},
        {'driver': 'GV4', 'value': 0, 'uom': 25},
    ]

    def getstationdata(self, ipaddr, username, password):
        """
            Here we assemble the url and template for the call to the Meteobridge
            and then unpack the returned data into variables. Simplified in Version 1.2.5 to
            streamline the basic auth method in requests.get
        """
        try:
            values = str(CreateTemplate())
            url = 'http://' + ipaddr + '/cgi-bin/template.cgi?template='
            LOGGER.debug("url in getstationdata: {}".format(url + values))

            u = requests.get(url + values, auth=(username, password))
            mbrdata = u.content.decode('utf-8')

        except OSError as err:
            LOGGER.error("Unable to connect to your MeteoBridge device")
            LOGGER.error(err)
            return

        mbrarray = mbrdata.split(" ")
        LOGGER.debug("mbrarray: {}".format(mbrarray))

        try:
            self.temperature = float(mbrarray[0])
            self.maxtemp = float(mbrarray[1])
            self.mintemp = float(mbrarray[2])
            self.dewpoint = float(mbrarray[3])
            self.windchill = float(mbrarray[4])

            self.rh = float(mbrarray[5])
            self.maxrh = float(mbrarray[6])
            self.minrh = float(mbrarray[7])

            self.stn_pressure = float(mbrarray[8])
            self.sl_pressure = float(mbrarray[9])
            self.pressure_trend = float(mbrarray[10])
            self.pressure_trend = self.pressure_trend + 1  # Meteobridge reports -1, 0, +1 for trends,converted for ISY

            try:
                self.uv = float(mbrarray[12])
                self.uvpresent = True

            except:  # no uv sensor
                self.uv = 0
                self.uvpresent = False

            try:
                self.solarradiation = float(mbrarray[11])
                self.et0 = float(mbrarray[13])
                self.vp2plus = True

            except:  # catch case where solar data is not available
                self.vp2plus = False
                self.solarradiation = 0
                self.et0 = 0

            self.wind = float(mbrarray[14])
            # wind = wind * 3.6 # the Meteobridge reports in mps, this is conversion to kph
            self.wind_gust = float(mbrarray[15])
            self.wind_dir = mbrarray[16]
            try:  # Meteobridge seems to sometimes return a nul string for wind0dir-act=endir
                # so we substitute the last good reading
                self.wind_dir_cardinal = self.wind_card_dict[mbrarray[17]]
                self.last_wind_dir = self.wind_dir_cardinal

            except:
                self.wind_dir_cardinal = self.last_wind_dir
                LOGGER.info("Cardinal wind direction substituted for last good reading: {}".format(self.last_wind_dir))

            LOGGER.debug(
                "mbr wind: {}, gust: {}, dir: {}, wdc: {}, wind_dir_cardinal: {}, last_wind_dir: {}".format(self.wind,
                                                                                                            self.wind_gust,
                                                                                                            self.wind_dir,
                                                                                                            mbrarray[
                                                                                                                17],
                                                                                                            self.wind_dir_cardinal,
                                                                                                            self.last_wind_dir))

            self.rain_rate = float(mbrarray[18])
            self.rain_today = float(mbrarray[19])
            self.rain_24hour = float(mbrarray[20])
            self.rain_yesterday = float(mbrarray[21])
            self.rain_month = float(mbrarray[22])
            self.rain_year = float(mbrarray[23])

            self.mbstation = mbrarray[24]
            self.mbstationnum = float(mbrarray[25])

            self.battery = int(float(mbrarray[26]))
            self.issbattery = int(float(mbrarray[27]))
            self.timestamp = int(mbrarray[28])
            self.lastgooddata = mbrarray[30]
            LOGGER.debug("Timestamp: {}, good data: {}".format(self.timestamp, self.lastgooddata))

        except ValueError or AttributeError as e:
            LOGGER.error("Error in getstationdata: {}".format(e))
            LOGGER.debug("Invalid value")
            LOGGER.debug(mbrarray)


class CreateTemplate:

    def __str__(self):
        mbtemplate = ""
        mbtemplatelist = [
            "[th0temp-act]",  # 0, current outdoor temperature
            "[th0temp-dmax]",  # 1, max outdoor temp today
            "[th0temp-dmin]",  # 2, min outdoor temp today
            "[th0dew-act]",  # 3, current outdoor dewpoint
            "[wind0chill-act]",  # 4 current windchill as calculated by MeteoBridge

            "[th0hum-act]",  # 5 current outdoor relative humidity
            "[th0hum-dmax]",  # 6 max outdoor relative humidity today
            "[th0hum-dmin]",  # 7 min outddor relative humidity today

            "[thb0press-act]",  # 8 current station pressure
            "[thb0seapress-act]",  # 9 current sealevel barometric pressure
            "[thb0press-delta3h=barotrend]",  # 10 pressure trend

            "[sol0rad-act]",  # 11 current solar radiation
            "[uv0index-act]",  # 12 current UV index
            "[sol0evo-daysum]",  # 13 today's cumulative evapotranspiration - Davis Vantage only

            "[wind0avgwind-act]",  # 14 average wind (depends on particular station)
            "[wind0wind-max10]",  # 15 10 minute wind gust
            "[wind0dir-act]",  # 16 current wind direction
            "[wind0dir-act=endir]",  # 17 current cardinal wind direction

            "[rain0rate-act]",  # 18 current rate of rainfall
            "[rain0total-daysum]",  # 19 rain accumulation for today
            "[rain0total-sum24h]",  # 20 rain over the last 24 hours
            "[rain0total-ydmax]",  # 21 total rainfall yesterday
            "[rain0total-monthsum]",  # 22 rain accumulation for this month
            "[rain0total-yearsum]",  # 23 rain accumulation year-to-date

            "[mbsystem-station]",  # 24 station id
            "[mbsystem-stationnum]",  # 25 meteobridge station number
            "[thb0lowbat-act]",  # 26 Station battery status (0=Ok, 1=Replace)
            "[th0lowbat-act]",  # 27 Station battery status (0=Ok, 1=Replace)

            #  "[UYYYY][UMM][UDD][Uhh][Umm][Uss]",  # 28 current observation time
            "[hh][mm][ss]",
            "[epoch]",  # 29 current unix time
            "[mbsystem-lastgooddata]",  # 30 seconds since last good data received from console
        ]

        for tempstr in mbtemplatelist:
            mbtemplate = mbtemplate + tempstr + "%20"

        return mbtemplate.strip("%20")
