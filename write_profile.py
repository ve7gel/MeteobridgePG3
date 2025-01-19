#!/usr/bin/env python3

import collections
from udi_interface import LOGGER
import os
import constants as uom

pfx = "write_profile:"

VERSION_FILE = "profile/version.txt"

# define templates for the various sensor nodes we have available. Each
# sensor node will have a pre-defined list of drivers. When we build
# the node definition, we get to pick which drivers we include based on
# the user's configuration.


NODEDEF_TMPL = "  <nodeDef id=\"%s\" nls=\"%s\">\n"
STATUS_TMPL = "      <st id=\"%s\" editor=\"%s\" />\n"


# As long as we provide proper dictionary lists for each type of node
# this will generate the node definitions.
#
# Assumes that the NLS exist for the nodes and that the editors exist.

def write_profile(temperature_list, humidity_list, pressure_list,
                  wind_list, rain_list, light_list, lightning_list):

    LOGGER.info("{0} Writing profile/nodedef/nodedefs.xml".format(pfx))
    if not os.path.exists("profile/nodedef"):
        try:
            os.makedirs("profile/nodedef")
        except:
            LOGGER.error('unable to create node definition directory.')

    nodedef = open("profile/nodedef/nodedefs.xml", "w")
    nodedef.write("<nodeDefs>\n")

    # First, write the controller node definition
    nodedef.write(NODEDEF_TMPL % ('meteobridge', 'ctl'))
    nodedef.write("    <sts>\n")
    nodedef.write("      <st id=\"ST\" editor=\"bool\" />\n")
    nodedef.write("      <st id=\"GV0\" editor=\"I_BATTERY\" />\n")
    nodedef.write("      <st id=\"GV1\" editor=\"I_BATTERY\" />\n")
    nodedef.write("      <st id=\"GV2\" editor=\"I_LAST_UPDATE\" />\n")
    nodedef.write("      <st id=\"GV3\" editor=\"I_SECONDS\" />\n")
    nodedef.write("    </sts>\n")
    nodedef.write("    <cmds>\n")
    nodedef.write("    <accepts>")
    nodedef.write("     </accepts>")
    nodedef.write("    </cmds>\n")
    nodedef.write("  </nodeDef>\n\n")

    # Need to translate temperature.main into <st id="ST" editor="TEMP_C" />
    # and     translate temperature.extra1 into <st id="GV5" editor="TEMP_C" />

    if len(temperature_list) > 0:
        nodedef.write(NODEDEF_TMPL % ('temperature', 'TEMP'))
        nodedef.write("    <sts>\n")
        for t in temperature_list:
            nodedef.write(STATUS_TMPL % (uom.TEMP_DRVS[t], temperature_list[t]))
        nodedef.write("    </sts>\n")
        nodedef.write("  </nodeDef>\n")

    if len(humidity_list) > 0:
        nodedef.write(NODEDEF_TMPL % ('humidity', 'HUM'))
        nodedef.write("    <sts>\n")
        for t in humidity_list:
            nodedef.write(STATUS_TMPL % (uom.HUMD_DRVS[t], humidity_list[t]))
        nodedef.write("    </sts>\n")
        nodedef.write("  </nodeDef>\n")

    if len(pressure_list) > 0:
        nodedef.write(NODEDEF_TMPL % ('pressure', 'PRESS'))
        nodedef.write("    <sts>\n")
        for t in pressure_list:
            nodedef.write(STATUS_TMPL % (uom.PRES_DRVS[t], pressure_list[t]))
        nodedef.write("    </sts>\n")
        nodedef.write("  </nodeDef>\n")

    if len(wind_list) > 0:
        nodedef.write(NODEDEF_TMPL % ('wind', 'WIND'))
        nodedef.write("    <editors   />\n")
        nodedef.write("    <sts>\n")
        for t in wind_list:
            nodedef.write(STATUS_TMPL % (uom.WIND_DRVS[t], wind_list[t]))
        nodedef.write("    </sts>\n")
        nodedef.write("  </nodeDef>\n")

    if len(rain_list) > 0:
        nodedef.write(NODEDEF_TMPL % ('precipitation', 'RAIN'))
        nodedef.write("    <sts>\n")
        for t in rain_list:
            nodedef.write(STATUS_TMPL % (uom.RAIN_DRVS[t], rain_list[t]))
        nodedef.write("    </sts>\n")
        nodedef.write("  </nodeDef>\n")

    if len(light_list) > 0:
        nodedef.write(NODEDEF_TMPL % ('light', 'LIGHT'))
        nodedef.write("    <sts>\n")
        for t in light_list:
            nodedef.write(STATUS_TMPL % (uom.LITE_DRVS[t], light_list[t]))
        nodedef.write("    </sts>\n")
        nodedef.write("  </nodeDef>\n")

    if len(lightning_list) > 0:
        nodedef.write(NODEDEF_TMPL % ('lightning', 'LIGHTNING'))
        nodedef.write("    <sts>\n")
        for t in lightning_list:
            nodedef.write(STATUS_TMPL % (uom.LTNG_DRVS[t], lightning_list[t]))
        nodedef.write("    </sts>\n")
        nodedef.write("  </nodeDef>\n")

    nodedef.write("</nodeDefs>")

    nodedef.close()

    LOGGER.info(pfx + " done.")

