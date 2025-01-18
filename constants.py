# version = "3.1.4"  # added error trapping to catch missing values from Meteobridge
# version = "3.2.0"  # added indoor readings to various node displays
version = "3.3.0"   # added et0 calculations for non-Vantage weather stations provide offer Solar Radiation values
                    # basic Penman-Monteith method.  Use with discretion

def cardinal_wind_dir_map(cardinal_dir):
    CARDINAL_WIND_DIR_MAP = {
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
    if cardinal_dir in CARDINAL_WIND_DIR_MAP:
        return CARDINAL_WIND_DIR_MAP[cardinal_dir]

    return 0


def mbtemplate():
    MBTEMPLATELIST = [
        "[th0temp-act]",  # 0, current outdoor temperature
        "[th0dew-act]",  # 1, current outdoor dewpoint
        "[wind0chill-act]",  # 2 current windchill as calculated by MeteoBridge
        "[th0temp-dmax]",  # 3, max outdoor temp today
        "[th0temp-dmin]",  # 4, min outdoor temp today
        "[thb0temp-act]",  # 5, indoor temperature
        "[thb0dew-act]",  # 6, indoor dew point

        "[th0hum-act]",  # 7 current outdoor relative humidity
        "[th0hum-dmax]",  # 8 max outdoor relative humidity today
        "[th0hum-dmin]",  # 9 min outddor relative humidity today
        "[thb0hum-act]",  # 10 indoor humidity

        "[thb0press-act]",  # 11 current station pressure
        "[thb0seapress-act]",  # 12 current sealevel barometric pressure
        "[thb0press-delta3h=barotrend]",  # 13 pressure trend

        "[sol0rad-act]",  # 14 current solar radiation
        "[uv0index-act]",  # 15 current UV index
        "[sol0evo-daysum]",  # 16 today's cumulative evapotranspiration - Davis Vantage only

        "[wind0avgwind-act]",  # 17 average wind (depends on particular station)
        "[wind0wind-max10]",  # 18 10 minute wind gust
        "[wind0dir-act]",  # 19 current wind direction
        "[wind0dir-act=endir]",  # 20 current cardinal wind direction

        "[rain0rate-act]",  # 21 current rate of rainfall
        "[rain0total-daysum]",  # 22 rain accumulation for today
        "[rain0total-sum24h]",  # 23 rain over the last 24 hours
        "[rain0total-ydmax]",  # 24 total rainfall yesterday
        "[rain0total-monthsum]",  # 25 rain accumulation for this month
        "[rain0total-yearsum]",  # 26 rain accumulation year-to-date

        "[mbsystem-station]",  # 27 station id
        "[mbsystem-stationnum]",  # 28 meteobridge station number
        "[thb0lowbat-act]",  # 29 Station battery status (0=Ok, 1=Replace)
        "[th0lowbat-act]",  # 30 Station battery status (0=Ok, 1=Replace)

        #  "[UYYYY][UMM][UDD][Uhh][Umm][Uss] ",  # 31 current observation time
        "[hh][mm][ss]",
        "[epoch]",  # 32 current unix time
        "[mbsystem-lastgooddata]",  # 33 seconds since last good data received from console

        # Lightning data added to accommodate Weatherflow Tempest and others
        "[lgt0total-daysum]", # 34 number of lightning strikes
        "[lgt0dist-davg]", # 35 distance to lightning strikes
    ]
    mbtemplate_tmp = ""
    # values = str(CreateTemplate())
    for tempstr in MBTEMPLATELIST:
        mbtemplate_tmp = mbtemplate_tmp + tempstr + "%20"

    mbtemplate_tmp.strip("%20")
    # Insert spaces between elements of the template to allow splitting the returned data, but no trailing space
    return mbtemplate_tmp


# Unit of Measure map
#
# Map the editor ID to the ISY UOM number

UOM = {
    'I_TEMP_C': 4,
    'I_TEMP_F': 17,
    'I_HUMIDITY': 51,
    'I_MB': 117,
    'I_INHG': 23,
    'I_TREND': 25,
    'I_KPH': 32,
    'I_MPH': 48,
    'I_DEGREE': 14,
    'I_MMHR': 46,
    'I_INHR': 24,
    'I_MM': 82,
    'I_INCHES': 105,
    'I_UV': 71,
    'I_LUX': 36,
    'I_RADIATION': 74,
    'I_STRIKES': 56,
    'I_KM': 83,
    'I_MILE': 116,
    'I_MPS': 40,
    'I_BATTERY': 25,
    'I_LAST_UPDATE': 56,
    'I_CARDINAL': 25,
}

TEMP_DRVS = {
    'main': 'ST',
    'dewpoint': 'GV0',
    'windchill': 'GV1',
    'heatindex': 'GV2',
    'apparent': 'GV3',
    'inside': 'GV4',
    'extra1': 'GV5',
    'extra2': 'GV6',
    'extra3': 'GV7',
    'extra4': 'GV8',
    'extra5': 'GV9',
    'extra6': 'GV10',
    'extra7': 'GV11',
    'extra8': 'GV12',
    'extra9': 'GV13',
    'dewin': 'GV14',
    'tempmax': 'GV15',
    'tempmin': 'GV16',
    'soil': 'GV17',
}

HUMD_DRVS = {
    'main': 'ST',
    'inside': 'GV0',
    'max': 'GV1',
    'min': 'GV2',
    'extra3': 'GV3',
    'extra4': 'GV4',
    'extra5': 'GV5',
}

PRES_DRVS = {
    'station': 'ST',
    'sealevel': 'GV0',
    'trend': 'GV1'
}

WIND_DRVS = {
    'windspeed': 'ST',
    'gustspeed': 'GV0',
    'winddir': 'GV1',
    'winddircard': 'GV2',
    'windspeed1': 'GV3',
    'gustspeed1': 'GV4',
}

RAIN_DRVS = {
    'rate': 'ST',
    'hourly': 'GV0',
    'daily': 'GV1',
    '24hour': 'GV2',
    'monthly': 'GV3',
    'yearly': 'GV4',
    'maxrate': 'GV5',
    'yesterday': 'GV6',
    'total': 'GV7'
}

LITE_DRVS = {
    'uv': 'ST',
    'solar_radiation': 'GV0',
    'luminance': 'GV1',
    'evapotranspiration': 'GV2'
}

LITE_EDIT = {
    'uv': 'I_UV',
    'solar_radiation': 'I_RADIATION',
    'luminance': 'I_LUX',
    'evapotranspiration': 'I_MM'
}

LTNG_DRVS = {
    'strikes': 'ST',
    'distance': 'GV0'
}
