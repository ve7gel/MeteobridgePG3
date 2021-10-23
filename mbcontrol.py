# !/usr/bin/env python3
import sys
import udi_interface
from nodes import meteobridge

if __name__ == "__main__":
    try:
        # Create an instance of the Polyglot interface. We need to
        # pass in array of node classes (or an empty array).
        polyglot = udi_interface.Interface([])

        # Initialize the interface
        polyglot.start()

        # Start the node server (I.E. create the controller node)
        control = meteobridge.Controller(polyglot, 'controller',  'controller', 'MeteoBridge')

        # Enter main event loop waiting for messages from Polyglot
        polyglot.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
