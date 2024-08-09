#Shutter_GUI v 2.0.0

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *

from labjack import ljm

import time
import sys
import os
import contextlib
import io

class Shutter_GUI(QtWidgets.QWidget):
#Some code derivted from pythonspot and ChatGPT
    def __init__(self):
        super().__init__()
        self.title = '3DShutter GUI'
        self.left = 10
        self.top = 10
        self.width = 800
        self.height = 450
        self.start()
        self.start_val=0


    def initialize(self):
        """
        Initializes connection to the Labjack
        """
        out = io.StringIO()
            with contextlib.redirect_stdout(out):
                with contextlib.redirect_stderr(out):
                    try:
                        handle = ljm.openS("T7", "ANY", "ANY")  # Switch T7 to whatever device that needs to be detected
                        info = ljm.getHandleInfo(handle)
                        print("Opened a LabJack with Device type: %i, Connection type: %i,\n"
                                  "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" %
                                  (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))
                            deviceType = info[0]
                        except Exception as e:
                            print(f"Error: {e}")
            self.output_window.setPlainText(out.getvalue())
        
    def start(self):
        """
        Establishes all non dynamic elements
        """
        self.num_of_shutters = 1 #initial val, only for start up - DO NOT CHANGE
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        #text box - number of shutters
        self.textbox = QLineEdit(self)
        self.textbox.move(20, 20)
        self.textbox.resize(100, 40)
        self.textbox.setPlaceholderText("# of Shutters")

        #submit - number of shutters
        self.button = QPushButton('Enter', self)
        self.button.move(20, 60)
        self.button.clicked.connect(self.read_shutters)
        
        #Output window will display command outputs and errors
        self.output_window = QTextEdit(self)
        self.output_window.setReadOnly(True) 
        self.output_window.setFixedSize(250, 300)
        self.output_window.setPlaceholderText("Output window (will display info)")
        self.output_window.move(20,90)
        
        #Exit button
        self.exit_button = QPushButton('Exit', self)
        self.exit_button.move(700,360)
        self.exit_button.clicked.connect(self.exit)
        


        self.show()

    def read_shutters(self):
        """
        Ensures that port related settings are only changed if needed
        """
        num=int(self.textbox.text())
        if self.num_of_shutters == num:
            print('You have entered same number of shutters')
        elif num <= 0:
            print('Error, number of shutters cannot be less than or equal to 0!')
        else:
            self.num_of_shutters=num
            self.set_ports(num)
            
        print(self.num_of_shutters)
        

    def set_ports(self, n):
        """
        Sets the ability to add/remove ports
        """
        #When changing the number of shutters after the first start up, this will delete all elements relating to ports
        if self.start_val==1:
            for i in range(len(self.ports)):
                self.ports[i].deleteLater()
                for j in range(2):
                    self.buttons[i][j].deleteLater()
            self.ports=[]
            self.buttons=[]
            self.labels=[]
            
        
        #Initialize vars
        self.ports=[[] for _ in range(n)]
        self.ports_names=[[] for _ in range(n)]
        self.labels=[[] for _ in range(n)]
        self.buttons=[[] for _ in range(n)]
        for i in range(n):
            self.buttons[i]=[[] for _ in range(2)]
        
        #Organizes the input buttons and text boxes - puts even values (from the loop) in the first column and odd values in the second column
        num_odd=40
        num_even=40
        for i in range(n):
            self.ports[i] = QLineEdit(self)
            self.buttons[i][0]=QPushButton('On', self)
            self.buttons[i][1]=QPushButton('Off', self)            
            if i % 2 == 1: #Odd
                #Port initialization
                self.ports[i].move(500, num_odd)
                self.ports[i].resize(150, 40)
                self.ports[i].setPlaceholderText("Port " + str(i+1))
                
                #Label initialization
                self.labels[i] = QLabel("Port " + str(i+1), self)
                self.labels[i].move(500, num_odd-20)
                
                #On/off button initialization
                self.buttons[i][0].move(500, num_odd+40)
                self.buttons[i][1].move(550, num_odd+40)
                
                #Button names - tells program what port to contorl and on/off
                self.buttons[i][0].setObjectName(str(i) + ",on")
                self.buttons[i][1].setObjectName(str(i) + ",off")
                
                num_odd+=100 #Sets the next location in this column to 100 points after
                
                #Show
                self.ports[i].show()
                self.labels[i].show()
                self.buttons[i][0].show()
                self.buttons[i][1].show()
                
            else: #Even
                #Text box initialization
                self.ports[i].move(310, num_even)
                self.ports[i].resize(150, 40)
                self.ports[i].setPlaceholderText("port " + str(i+1))
                
                #Label initialization
                self.labels[i] = QLabel("Port " + str(i+1), self)
                self.labels[i].move(310, num_odd-20)
                
                #On/off button initialization
                self.buttons[i][0].move(310, num_even+40)
                self.buttons[i][1].move(360, num_even+40)
                
                #Button names - tells program what port to contorl and on/off
                self.buttons[i][0].setObjectName(str(i) + ",on")
                self.buttons[i][1].setObjectName(str(i) + ",off")
                
                num_even+=100 #Sets the next box location in this column to 100 points after

                #Show
                self.ports[i].show()
                self.labels[i].show()
                self.buttons[i][0].show()
                self.buttons[i][1].show()
                
        
        self.start_val=1 #Tells the program to delete existing elements if new number of shutters is established
        
        #When clicked...
        for i in range(n):
            for j in range(2):
                self.buttons[i][j].clicked.connect(self.clicked)
                
                
    def clicked(self):
        """
        On and off controller
        """
        button=self.sender() #Gets info about what element activated this function
        name=button.objectName()
        
        output=name.split(",") #Splits output to get port and on/off
        
        port=str(self.ports[int(output[0])])
        for i in range(len(self.ports)): #Reads all text boxes giving port names
            self.ports_names[i]=self.ports[i].text()
            
        
        #Turns the port on/off, raises an error if there an issue -> output to command window
        if output[1]=="on":
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                with contextlib.redirect_stderr(out):
                    try:
                        ljm.eWriteName(handle, self.ports_names[int(output[0])], 1)
                        print("Port "  + self.ports_names[int(output[0])] + " turned on")
                    except Exception as e:
                        print(f"Error: {e}")
            self.output_window.setPlainText(out.getvalue())
            
        else:
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                with contextlib.redirect_stderr(out):
                    try:
                        ljm.eWriteName(handle, self.ports_names[int(output[0])], 0)
                        print("Port "  + self.ports_names[int(output[0])] + " turned off")
                    except Exception as e:
                        print(f"Error: {e}")
            self.output_window.setPlainText(out.getvalue())
        
        
    def exit(self):
        """
        Exit function, closes connection to the Labjack and closes the GUI
        """
        ljm.close(handle)
        sys.exit(app.exec())
            
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = Shutter_GUI()
    sys.exit(app.exec())
