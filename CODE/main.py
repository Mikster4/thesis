# Importing Libraries
from serial import Serial
import time
import asyncio
import math
from math import cos, sin, radians
import matplotlib.pyplot as plt
import numpy as np

# Class for Air Module
class AirModule:
    # Constructor for Air Module
    def __init__(self, base_module, address, pIn, pOut):
        # Assigning the base module
        self.base_module = base_module

        # Assigning the address
        self.address = address

        # Adding the air module to the base module
        self.base_module.air_modules.append(self)

        # Digital pins for input and output
        self.dig_in = pIn
        self.dig_out = pOut

    def __repr__(self):
        return "AirModule()"

    def __str__(self):
        return "Air Module"

    # Function to open the input valve for given time
    async def inflate(self, time):
        self.base_module.write(bytes([0xFF, 0x03, hex(self.dig_in)]))
        await asyncio.sleep(time)
        self.base_module.write(bytes([0xFF, 0x03, 0x10 + hex(self.dig_in)]))

    # Function to open the output valve for given time
    async def deflate(self, time):
        self.base_module.write(bytes([0xFF, 0x03, hex(self.dig_out)]))
        await asyncio.sleep(time)
        self.base_module.write(bytes([0xFF, 0x03, 0x10 + hex(self.dig_out)]))


# Class for base module
class BaseModule:
    # Constructor for Base Module
    def __init__(self):
        # Creating a serial connection to the arduino
        # self.arduino = Serial(port="/dev/ttyACM0", baudrate=115200, timeout=0.1)
        print("Arduino connected. Wating for 4 seconds to start.")
        #time.sleep(3)

        # Lift of tuples for input and output pins for each air module
        self.air_pins = [(2, 3), (4, 5), (6, 7), (8, 9), (10, 11), (12, 13)]

        self._adc_address = [0x48, 0x49]
        
        # List of assigned Air Modules
        self.air_modules = [None] * 6
        for i in range(1, 7):
            self.add_air_module(i)


    def __repr__(self):
        return "BaseModule()"

    def __str__(self):
        return "Base Module\nAir Modules: " + str(self.air_modules) + "\n"

    # Quick initialization
    def quick_init(self):
        # Opens the input valve for all air modules for brief period
        for p in self.air_pins:
            self.write_bytes(bytearray([0x10, 0x40 + p[0], 0x11]))
        time.sleep(0.1)
        for p in self.air_pins:
            self.write_bytes(bytearray([0x10, 0x50 + p[0], 0x11]))
        time.sleep(0.1)
        
        # Opens the output valve for all air modules for longer period to remove air
        for p in self.air_pins:
            self.write_bytes(bytearray([0x10, 0x40 + p[1], 0x11]))
        time.sleep(1)
        for p in self.air_pins:
            self.write_bytes(bytearray([0x10, 0x50 + p[1], 0x11]))
            

    # Fancy initialization
    def fancy_init(self):
        # Opens the input valve for all air modules for brief period
        for p in self.air_pins:
            self.write_bytes(bytearray([0x10, 0x40 + p[0], 0x11]))
            time.sleep(0.1)
            self.write_bytes(bytearray([0x10, 0x50 + p[0], 0x11]))
            time.sleep(0.1)
        time.sleep(0.4)

        # Opens the output valve for all air modules for longer period to remove air
        for p in self.air_pins:
            self.write_bytes(bytearray([0x10, 0x40 + p[1], 0x11]))
            time.sleep(0.5)
            self.write_bytes(bytearray([0x10, 0x50 + p[1], 0x11]))
            time.sleep(0.5)

    def write_bytes(self, data):
        self.arduino.write(data)

    def read_bytes(self):
        s = self.arduino.readline().decode("utf-8")[:-1]
        return s

    def _is_valid_connection(self, connector):
        if connector > 6 or connector < 1:
            print("Invalid connector number.")
            return False
        if self.air_modules[connector - 1] != None:
            print("Air Module already added at connector ", connector)
            return False
        return True

    # Function to add an air module based on connection index
    def add_air_module(self, connector):
        # Checking if the connector is valid
        if not self._is_valid_connection(connector):
            return

        adc = 0x48 if connector <= 4 else 0x49
        air_module = AirModule(
            self, adc, self.air_pins[connector - 1][0], self.air_pins[connector - 1][1]
        )

        self.air_modules[connector] = air_module

        print("Air Module added at connector ", connector)

    # Function to remove an air module based on connection index
    def remove_air_module(self, connector):
        # Checking if the connector is valid
        if not self._is_valid_connection(connector):
            return

        # Removing the air module from the list
        self.air_modules.pop(connector - 1)

        print("Air Module removed from connector ", connector)

    # Report air pressure from given air module
    def report_air_pressure(self, connector):
        # Checking if the connector is valid
        if not self._is_valid_connection(connector):
            return

        # Sending the command to arduino
        self.arduino.write(bytes("3", "utf-8"))

        # Reading the pressure
        pressure = self.arduino.readline().decode()

        print("Pressure at connector ", connector, " is ", pressure)

    def _x_rotation(self,vector,theta):
        """Rotates 3-D vector around x-axis"""
        R = np.array([[1,0,0],[0,np.cos(theta),-np.sin(theta)],[0, np.sin(theta), np.cos(theta)]])
        return np.dot(R,vector)

    def _y_rotation(self,vector,theta):
        """Rotates 3-D vector around y-axis"""
        R = np.array([[np.cos(theta),0,np.sin(theta)],[0,1,0],[-np.sin(theta), 0, np.cos(theta)]])
        return np.dot(R,vector)

    def _z_rotation(self,vector,theta):
        """Rotates 3-D vector around z-axis"""
        R = np.array([[np.cos(theta), -np.sin(theta),0],[np.sin(theta), np.cos(theta),0],[0,0,1]])
        return np.dot(R,vector)

    """Calculates the position of the legs based on the given T and R values"""
    def calculate_legs(self, T, R, plot=False):
        R = np.array([radians(r) for r in R])
        
        # Distance from center of base to center of connected pistons
        dist = 86.493
        # Angle between the pistons
        angle = radians(10.7)
        
        third = 2 * math.pi / 3

        # Calculate the position of attachment points on the base
        b1 = cos(third * 0 + angle) * dist, sin(third * 0 + angle) * dist, 0
        b2 = cos(third * 1 - angle) * dist, sin(third * 1 - angle) * dist, 0
        b3 = cos(third * 1 + angle) * dist, sin(third * 1 + angle) * dist, 0
        b4 = cos(third * 2 - angle) * dist, sin(third * 2 - angle) * dist, 0
        b5 = cos(third * 2 + angle) * dist, sin(third * 2 + angle) * dist, 0
        b6 = cos(third * 3 - angle) * dist, sin(third * 3 - angle) * dist, 0


        b = np.array([b1, b2, b3, b4, b5, b6])

        # Calculate the position of the attachment points on the platform
        q1 = np.array([cos(third * 0.5 + angle) * dist, sin(third * 0.5 + angle) * dist, 0])
        q2 = np.array([cos(third * 0.5 - angle) * dist, sin(third * 0.5 - angle) * dist, 0])
        q3 = np.array([cos(third * 1.5 + angle) * dist, sin(third * 1.5 + angle) * dist, 0])
        q4 = np.array([cos(third * 1.5 - angle) * dist, sin(third * 1.5 - angle) * dist, 0])
        q5 = np.array([cos(third * 2.5 + angle) * dist, sin(third * 2.5 + angle) * dist, 0])
        q6 = np.array([cos(third * 2.5 - angle) * dist, sin(third * 2.5 - angle) * dist, 0])

        q = np.array([q1, q2, q3, q4, q5, q6])

        # Translate and rotate the attachment points according to the given T and R values
        q = [T + self._z_rotation(self._y_rotation(self._x_rotation(q_i, R[0]), R[1]), R[2]) for q_i in q]
        
        if plot:
        # Plots the base
            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')
            for b_i in b:
                ax.scatter(b_i[0], b_i[1], b_i[2], c='b', marker='o')
            
            for q_i in q:
                ax.scatter(q_i[0], q_i[1], q_i[2], c='r', marker='o')
            
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.set_zlabel('Z')
            plt.show()

        # Length of the legs
        l = [ q_i - np.array(b[i]) for i, q_i in enumerate(q)]
        return [ np.sqrt(l_i[0]**2 + l_i[1]**2 + l_i[2]**2) for l_i in l]
        



if __name__ == "__main__":
    bm = BaseModule()

    len = bm.calculate_legs([0, 0, 52], [0, 0, 0], plot=True)
    len = bm.calculate_legs([23, 18.2, 67], [12.9, 9.02, 14.5], plot=True)
    print(len)
    
    bm.fancy_init()

    while True:
        data = bm.read_bytes()
        if data:
            print(data)
