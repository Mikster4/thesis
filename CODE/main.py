# Importing Libraries
from serial import Serial
import time


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
        def inflate(self, time):
            self.base_module.write(bytes([0xFF, 0x03, hex(self.dig_in)]))
            time.sleep(time)
            self.base_module.write(bytes([0xFF, 0x03, 0x10 + hex(self.dig_in)]))

        # Function to open the output valve for given time
        def deflate(self, time):
            self.base_module.write(bytes([0xFF, 0x03, hex(self.dig_out)]))
            time.sleep(time)
            self.base_module.write(bytes([0xFF, 0x03, 0x10 + hex(self.dig_out)]))


# Class for base module
class BaseModule:
    # Constructor for Base Module
    def __init__(self):
        # Creating a serial connection to the arduino
        self.arduino = Serial(port="/dev/ttyACM0", baudrate=115200, timeout=0.1)
        print("Arduino connected. Wating for 4 seconds to start.")
        time.sleep(3)

        # List of assigned Air Modules
        self.air_modules = [None] * 6

        # Lift of tuples for input and output pins for each air module
        self.air_pins = [(2, 3), (4, 5), (6, 7), (8, 9), (10, 11), (12, 13)]

        self._adc_address = [0x48, 0x49]

    def __repr__(self):
        return "BaseModule()"

    def __str__(self):
        return "Base Module\nAir Modules: " + str(self.air_modules) + "\n"
    
    # Fancy initialization
    def fancy_init(self):
        # Opens the input valve for all air modules for brief period
        for p in self.air_pins:
            self.write_bytes(bytearray([0x10,0x40 + p[0],0x11]))
            time.sleep(0.1)
            self.write_bytes(bytearray([0x10,0x50 + p[0],0x11]))
            time.sleep(0.1)
        time.sleep(0.4)

        # Opens the output valve for all air modules for longer period to remove air
        for p in self.air_pins:
            print(p[1])
            self.write_bytes(bytearray([0x10,0x40 + p[1],0x11]))
            time.sleep(0.5)
            self.write_bytes(bytearray([0x10,0x50 + p[1],0x11]))
            time.sleep(0.5)



        
            
    


    def write_bytes(self, data):
        self.arduino.write(data)

    def read_bytes(self):
        s = self.arduino.readline().decode("utf-8")
        return s

    def _is_valid_connection(self, connector):
        if connector >= 6 or connector <= 1:
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


# BOM
# 0x10   - Start of message
# 0x3X   - Read pressure from air module X
# 0x4X   - Open input valve at pin X
# 0x5X   - Close input valve at pin X
# 0x6X   - Open output valve at pin X
# 0x7X   - Close output valve at pin X
# 0x11   - End of message



if __name__ == "__main__":
    bm = BaseModule()
    # bm.write_bytes(bytes("1", "utf-8"))
    #bm.read_bytes()
    
    #bm.write_bytes(bytearray([0x10,0x32,0x11]))
    #bm.write_bytes(bytearray([0x10,0x35,0x11]))
    
    bm.fancy_init()
    

    


    while True:
        data = bm.read_bytes()
        if data:
            print(data)
            