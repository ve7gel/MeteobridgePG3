# !/usr/bin/env python3
import sys
from udi_interface import Interface
from nodes import Controller
version = '3.1.2'

if __name__ == "__main__":
    try:
        # Create an instance of the Polyglot interface. We need to
        # pass in array of node classes (or an empty array).
        polyglot = Interface([Controller])

        # Initialize the interface
        polyglot.start(version)

        # Start the node server (I.E. create the controller node)
        control = Controller(polyglot, 'controller', 'controller', 'Meteobridge')

        # Enter main event loop waiting for messages from Polyglot
        polyglot.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
