import sys
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import io
import contextlib
from labjack import ljm
import time


class CodeOutputWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.numFrames = []
        self.aNames = []
        self.pwmDIO = []
        self.initialize_vars()
        self.initUI()

    def initialize_vars(self):
        ports = ["DIO0", "DIO2"]
        self.pwmDIO = [[] for _ in range(len(ports))]
        self.aNames = [[] for _ in range(len(ports))]
        self.numFrames = [[] for _ in range(len(ports))]
        self.results = [[] for _ in range(len(ports))]

        for i in range(len(ports)):
            self.pwmDIO[i] = int(ports[i][-1])

        for i in range(len(ports)):
            self.aNames[i] = ["DIO_EF_CLOCK0_DIVISOR", "DIO_EF_CLOCK0_ROLL_VALUE",
                              "DIO_EF_CLOCK0_ENABLE", "DIO%i_EF_ENABLE" % self.pwmDIO[i],
                              "DIO%i_EF_INDEX" % self.pwmDIO[i], "DIO%i_EF_CONFIG_A" % self.pwmDIO[i],
                              "DIO%i_EF_ENABLE" % self.pwmDIO[i], "DIO18_EF_ENABLE",
                              "DIO18_EF_INDEX", "DIO18_EF_ENABLE"]

        for i in range(len(ports)):
            self.numFrames[i] = len(self.aNames[i])

        aValues = [1, 8000, 1, 0, 0, 2000, 1, 0, 7, 1]

    def initUI(self):
        self.resize(800, 600)

        # Create a central widget and set layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)  # Main horizontal layout

        # Create a vertical layout for buttons and spinner
        right_layout = QVBoxLayout()

        self.spin_label = QLabel('Number of Ports Used (for PWM output):', self)
        right_layout.addWidget(self.spin_label)

        # Create a QTextEdit widget for output
        self.text_edit = QTextEdit(self)
        self.text_edit.setReadOnly(True)  # Set it to read-only so the user can't modify the output
        self.text_edit.setFixedSize(600, 400)  # Make the text output box smaller
        main_layout.addWidget(self.text_edit)

        # Create a QSpinBox
        self.spin = QSpinBox(self)
        self.spin.setMaximum(100)  # Example maximum value
        self.spin.setFixedSize(100, 40)
        right_layout.addWidget(self.spin)

        # Create QPushButtons to execute code
        self.run_button_up = QPushButton('Up', self)
        self.run_button_up.clicked.connect(lambda: self.mv_output_capture(0))
        right_layout.addWidget(self.run_button_up)

        self.run_button_down = QPushButton('Down', self)
        self.run_button_down.clicked.connect(lambda: self.mv_output_capture(1))
        right_layout.addWidget(self.run_button_down)

        self.run_button_exit = QPushButton('Exit Code', self)
        self.run_button_exit.clicked.connect(self.exit_program)
        right_layout.addWidget(self.run_button_exit)

        # Add the right layout to the main layout
        main_layout.addLayout(right_layout)

        # Set the main window properties
        self.setWindowTitle('Code Output Window')

        global handle, info, deviceType
        handle = ljm.openS("T7", "ANY", "ANY")  # Switch T7 to whatever device that needs to be detected
        info = ljm.getHandleInfo(handle)
        self.initialize()

        self.power(1000, ljm.constants.FLOAT32, 5)

    def initialize(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            with contextlib.redirect_stderr(output):
                try:
                    print("Opened a LabJack with Device type: %i, Connection type: %i,\n"
                          "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" %
                          (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))
                    deviceType = info[0]
                except Exception as e:
                    print(f"Error: {e}")
        self.text_edit.setPlainText(output.getvalue())

    def power(self, address, dataType, value):  # 5 volts needed to power H bridge
        ljm.eWriteAddress(handle, address, dataType, value)
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            with contextlib.redirect_stderr(output):
                try:
                    print("5 volts output")
                except Exception as e:
                    print(f"Error: {e}")
        self.text_edit.setPlainText(output.getvalue())

    def mv_output_capture(self, var):
        # Capture the code output
        out = var
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            with contextlib.redirect_stderr(output):
                try:

                    result = self.movement_output(out)
                except Exception as e:
                    print(f"Error: {e}")

        # Display the output in the QTextEdit
        self.text_edit.setPlainText(output.getvalue())

    def movement_output(self, var):
        # Example code to be executed
        if var == 0:
            self.move(0)
            print("Moved up\n")
        elif var == 1:
            self.move(1)
            print("Moved down\n")
        else:
            print(f"error!\n")
        print(var)

    def move(self, n):
        aValues = [1, 8000, 1, 0, 0, 2000, 1, 0, 7, 1]
        ljm.eWriteNames(handle, self.numFrames[n], self.aNames[n], aValues)
        time.sleep(.5)
        ljm.eWriteNames(handle, self.numFrames[n], self.aNames[n], [0, 0])

    def exit_program(self):
        alert = QMessageBox()
        alert.setText('Are you sure you want to exit?')
        alert.exec()
        for i in range(len(ports)):
            aNames[i] = ["DIO_EF_CLOCK0_ENABLE", "DIO%i_EF_ENABLE" % self.pwmDIO[i]]
            aValues = [0, 0]
            numFrames[i] = len(aNames[i])
            ljm.eWriteNames(self.handle, numFrames[i], aNames[i], aValues)
        # Close handle
        self.power(1000, ljm.constants.FLOAT32, 0)
        ljm.close(handle)
        sys.exit(app.exec_())

    def show_result(self):
        # setting value of spin box to the label
        num_ports = self.spin.value()


if __name__ == '__main__':
    App = QApplication(sys.argv)

    # create the instance of our Window
    window = CodeOutputWindow()

    window.show()
    # start the app
    sys.exit(App.exec())
