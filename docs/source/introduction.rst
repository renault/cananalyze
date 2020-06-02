Introduction
============

CANanalyze is a Python3 library to interact with automotive protocols like CAN, ISOTP, UDS. Renault & Thales have developed this framework to easily  interact with an  ECU. The framework can be used in different scenarios:

* Interact with automotive protocols like CAN/ISOTP/UDS, if you want to extract/change some ECU configurations.
* Detect if some UDS debug services are still enabling like the readMemory service.
* Test gateway calibration.


Supported hardware
------------------

The framework was designed to interact with the komodo or all devices supported by the python-can lib:

* Socketcan
* CAN over Serial / SLCAN
* Vector
* ...

Note that when using an interface supported by the python-can library, the CAN-FD capabilities are enabled (when using a compliant interface).

This framework was essentially tested with the Komodo and CANUSB device.

Tutorial
--------

Create context
^^^^^^^^^^^^^^
When you want to send some frame (CAN/ISOTP/UDS). Firstly, you need to create a session specifying:

* Used hardware (komodo, socketcan)
* CAN speed
* sending CANid
* receiving CANid
* timeout

Context: Example with the Komodo
""""""""""""""""""""""""""""""""

Lets take an example, if you use a komodo and you want to create your context

.. code-block:: python

        import cananalyze.context as context
        ctx = context.create_ctx (channel = 'A', bustype = context.BusType.KOMODO, port_nr = 0, bitrate = 500000, canid_recv = 0x7DA, canid_send = 0x7cA, timeout = 1)


Context: Example with socketCan
"""""""""""""""""""""""""""""""

After plugging your interface, you need to mount it.

.. code-block:: bash

        sudo modprobe can
        sudo modprobe can_raw
        sudo modprobe slcan
        echo "You have to choose the speed -s6 for 500kbits/s -s4 for 125Kbit/s and ttyUBSX"
        sudo slcand -o -c -f -s6 /dev/ttyUSB1 slcan0
        sudo ifconfig slcan0 up

After configuring your interface you can finally create your context

.. code-block:: python

        import cananalyze.context as context
        ctx = context.create_ctx (channel = 'vcan0', bustype = context.BusType.SOCKETCAN, bitrate = 500000, canid_recv = 0x7da, canid_send = 0x7ca, timeout = 1)

Context: Example with Vector
""""""""""""""""""""""""""""

Before the beginning of the configuration, make sure you installed the Vector's driver available on `Vector's official website <https://www.vector.com>`_.

Once this is done you will need to configure a new application in the ``Vector Hardware`` configuration window available in the ``Hardware and Sound`` category of your ``Control Panel``.

Inside the ``Vector Hardware`` wizard, add an application called python-can and assign it the desired number of channels.

Before exiting the ``Vector Hardware`` wizard, you need to map the Vector's physical I/O to virtual channels.

You can now use CANanalyze with your Vector:

.. code-block:: python

        import cananalyze.context as context
        ctx = context.create_ctx (channel = '0', bustype = context.BusType.VECTOR, bitrate = 5000000, canid_recv = 0x7da, canid_send = 0x7ca, timeout = 1)

Note that the channel number passed as a create_ctx's parameter correspond to the interfaces order presented in your created application inside the ``Vector Hardware`` wizard.

Sending Frame
"""""""""""""

After creating the context, you can send the frame you want

.. code-block:: python

        import cananalyze.abstract_can as vcan
        import cananalyze.uds as uds
        import cananalyze.context as context
        from cananalyze.tools import *


        if __name__ == "__main__":
            ctx = context.create_ctx (channel = 'A', bustype = context.BusType.KOMODO, port_nr = 0, bitrate = 500000, canid_recv = 0x7da, canid_send = 0x7ca, timeout = 1)
            #ctx = context.create_ctx (channel = 'vcan0', bustype = context.BusType.SOCKETCAN, bitrate = 500000, canid_recv = 0x7da, canid_send = 0x7ca, timeout = 1)

            ret = -1
            while ret != 0 :
                uds.write (ctx, [0x10, 0x03])
                ret, data = uds.read(ctx, "session", 0x10)

            print(hex_array(data))

Licensing
---------

CANanalyze is distributed under the "GNU Lesser General Public License v3.0" Licence by RENAULT / Thales 

