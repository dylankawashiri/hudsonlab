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

### Circuit

### STL Files
The STL files for 3D printing can be found in the ['STL Files' folder](https://github.com/dylankawashiri/hudsonlab/tree/main/3D%20Printed%20Shutter/STL%20Files).


## Python functions - Labjack
The native Kipling software can be used to give the Labjack commands. However, you can also use Python to execute commands. 

### Initiate connection
You first need to connect to the Labjack using the 'labjack.openS' command as seen below:

```
import labjack as ljm

handle = ljm.openS("ANY", "ANY", "ANY")
```
The first parameter of the openS function tells the program what Labjack device to search for. Leaving this, and the rest of the parameters, as "ANY" will result in your computer connecting to the first Labjack device found. If an error arises during this process, it is highly possible that another computer is accessing the Labjack. 

### Send a signal

To send a signal, the 'labjack.eWriteName' function. The parameters for this function are the handle, the port, and the value to set the output of the port, as seen below:

```
ljm.eWriteName(handle, DIO0, 1)
```

For the FIO/DIO ports (Digital Input/Output), you will set the value to either 1 or 0 (on or off). For the DAC ports (Digital to Analog Converter), you can set a voltage level (ie. 5.0 for 5 volts):

```
ljm.eWriteName(handle, DAC0, 5.0)
```

### Close connection

After you finish using the Labjack, it is important to close the connection. This can be done by simply executing the command:

```
ljm.close(handle)
```
Before doing this, you should set all outputs to 0. 


## GUI
You can see an example GUI in the [Python folder](https://github.com/dylankawashiri/hudsonlab/tree/main/3D%20Printed%20Shutter/Python).
<img width="799" alt="Screenshot 2024-08-09 at 10 54 53 PM" src="https://github.com/user-attachments/assets/fee356b1-9b60-4a15-a8da-b6067b0a1cb4">

## Notes
- Keep the supplied voltage for every component at 2.5 volts. If using a DAC input for the TTL signal, you can set the TTL output to 1.5 volts and it will still flip. The inverter and motor driver both need 2.5 volts to run properly.
- If you are using a higher voltage, make sure to turn off the supply voltage for the motor driver (and inverter) after it has moved. Forcibly stopping the motor will heat it up to over 60 degrees Celcius (which will melt the 3D printed materials and hot glue).
- Keeping the supply current to the motor driver above .05-.08 amps will allow for switching
