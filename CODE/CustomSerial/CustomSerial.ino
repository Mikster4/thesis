#include <ADS1115_WE.h>
#include <Wire.h>

// Addresses for the ADS1115
#define I2C_ADDRESS_1 0x48
#define I2C_ADDRESS_2 0x49

ADS1115_WE adc_1 = ADS1115_WE(I2C_ADDRESS_1);
ADS1115_WE adc_2 = ADS1115_WE(I2C_ADDRESS_2);

const int BUFFER_SIZE = 50;
char buf[BUFFER_SIZE];

void setup() {
  Wire.begin();
  Serial.begin(115200);
  
  for (int i = 2; i <= 13; i++) {
    pinMode(i, OUTPUT);
    digitalWrite(i, LOW);
  }

  while (!Serial) {
    ;  // wait for serial port to connect. Needed for native USB port only
  }
  if (!adc_1.init()) {
    Serial.print("ADS1115 No 1 not connected!");
  }
  adc_1.setVoltageRange_mV(ADS1115_RANGE_6144);
  //adc_1.setMeasureMode(ADS1115_CONTINUOUS);
  adc_1.setCompareChannels(ADS1115_COMP_0_GND);

  if (!adc_2.init()) {
    Serial.print("ADS1115 No 2 not connected!");
  }
  adc_2.setVoltageRange_mV(ADS1115_RANGE_6144);
  //adc_2.setMeasureMode(ADS1115_CONTINUOUS);
  adc_2.setCompareChannels(ADS1115_COMP_0_GND);
}

void readMessage() {
  const int buf_size = 20;
  char buf[buf_size];

  int n = Serial.readBytesUntil(0x11, buf, buf_size);

  for (int i = 0; i < n; i++) {
    // Handle pressure sensing
    if (buf[i] <= 0x3F) {
      Serial.println("Reading from sensor " + String(buf[i] % 0x30));

      // Set comparator
      switch (buf[i] % 0x30) {
        case 0:
          adc_2.setCompareChannels(ADS1115_COMP_3_GND);
          break;
        case 1:
          adc_1.setCompareChannels(ADS1115_COMP_0_GND);
          break;
        case 2:
          adc_1.setCompareChannels(ADS1115_COMP_1_GND);
          break;
        case 3:
          adc_1.setCompareChannels(ADS1115_COMP_2_GND);
          break;
        case 4:
          adc_1.setCompareChannels(ADS1115_COMP_3_GND);
          break;
        case 5:
          adc_2.setCompareChannels(ADS1115_COMP_0_GND);
          break;
        case 6:
          adc_2.setCompareChannels(ADS1115_COMP_1_GND);
          break;
      }

      float voltage = 0.0;
      // Do the meassurement
      if (buf[i] >= 0x30 && buf[i] <= 0x3F && buf[i] % 0x30 >= 1 && buf[i] % 0x30 <= 4) {
        adc_1.startSingleMeasurement();
        voltage = adc_1.getResult_mV();
      } else {
        adc_2.startSingleMeasurement();
        voltage = adc_2.getResult_mV();
      }
      Serial.println("Voltage: " + String(voltage));
    }

    // Handle opening of input valves
    if (buf[i] <= 0x4F) {
      digitalWrite(buf[i] % 0x40, HIGH);
    }

    // Handle closing of input valves
    if (buf[i] <= 0x5F) {
      digitalWrite(buf[i] % 0x50, LOW);
    }

    // Handle opening of output valves
    if (buf[i] <= 0x6F) {
      digitalWrite(buf[i] % 0x60, HIGH);
    }

    // Handle closing of output valves
    if (buf[i] <= 0x6F) {
      digitalWrite(buf[i] % 0x60, LOW);
    }
  }
}

void loop() {
  if (Serial.available() > 0) {
    char data = Serial.read();
    char str[2];
    switch (data) {
      case 0x10:
        //Serial.println("Message started");
        readMessage();
        //Serial.println("Message ended.");
        break;
      default:
        str[0] = data;
        str[1] = '\0';
        Serial.print(str);
        break;
    }
  }
}
