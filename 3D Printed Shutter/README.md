# 3D Printed Shutter
This README file goes over how to implement 3D-printed shutters using a Labjack T7-Pro

## Physical Shutter and Circuit
### Parts
- 3D Printed Shutter (Body and Blade)
- 4x 4.7 kOhm Resistors
- 2x DRV8833 Motor Drive Module
- 1x SN74LS06N Inverter
- 1x PNN7RE08JD DC Motor
- 8x 50 Ohm Resistors
- 1x Acopian 5 Volt, .7 Amp AC to DC Power Supply
- Labjack T7-Pro

While these are the items and parts I used, many of these parts can be interchanged, most notably the 50 Ohm resistors and the power supplied to the circuit. Although many of these parts are rated for 5 volts, they can be operated with around 2.5 volts. Additionally, the 50 Ohm resistors are in place to prevent the motor from heating up at the cost of reducing speed. 

### Circuit

![Untitled Notebook (223)-2](https://github.com/user-attachments/assets/ecdfd4d1-76ba-4ced-8aaa-5a1eddeaf142)

Drawn-out circuit diagram for one of the four motor controllers. With these components, you can attach and control up to four motors/shutters.

### STL Files

The STL files for 3D printing can be found in the ['STL Files' folder](https://github.com/dylankawashiri/hudsonlab/tree/main/3D%20Printed%20Shutter/STL%20Files).

## Shutter GUI
I have developed a GUI based on the PyQT library to control the shutter/Labjack combination, see the [Python](https://github.com/dylankawashiri/hudsonlab/tree/main/3D%20Printed%20Shutter/Python) folder for more information. The rest of this README will focus on the Python commands needed to control the Labjack and shutter(s) if you choose not to use the GUI. You can see an example GUI in the [Python folder](https://github.com/dylankawashiri/hudsonlab/tree/main/3D%20Printed%20Shutter/Python).
<img width="799" alt="Screenshot 2024-08-09 at 10 54 53 PM" src="https://github.com/user-attachments/assets/fee356b1-9b60-4a15-a8da-b6067b0a1cb4">

Screenshot of the GUI. 

## Python functions - Labjack
The native Kipling software can be used to give the Labjack commands. However, you can also use Python to execute commands. 

### Initiate connection
You first need to connect to the Labjack using the 'labjack.openS' command as seen below:

```python
import labjack as ljm

handle = ljm.openS("ANY", "ANY", "ANY")
```
The first parameter of the openS function tells the program what Labjack device to search for. Leaving this, and the rest of the parameters, as "ANY" will result in your computer connecting to the first Labjack device found. If an error arises during this process, it is highly possible that another computer is accessing the Labjack. 

### Send a signal

To send a signal, the 'labjack.eWriteName' function. The parameters for this function are the handle, the port, and the value to set the output of the port, as seen below:

```python
ljm.eWriteName(handle, DIO0, 1)
```

For the FIO/DIO ports (Digital Input/Output), you will set the value to either 1 or 0 (on or off). For the DAC ports (Digital to Analog Converter), you can set a voltage level (ie. 5.0 for 5 volts):

```python
ljm.eWriteName(handle, DAC0, 5.0)
```

### Close connection

After you finish using the Labjack, it is important to close the connection. This can be done by simply executing the command:

```python
ljm.close(handle)
```
Before doing this, you should set all outputs to 0 otherwise they will continue to output a signal. 



## Notes
- Keep the supplied voltage for every component at 2.5 volts (minimum). If using a DAC input for the input signal, you can set the output to 1.5 volts and the shutter will still flip. 
- With this circuit, not having the terminating resistor resulted in 
- Keeping the supply current to the motor driver above .05-.08 amps will allow for switching
