#include <QMC5883LCompass.h>
#include <Wire.h>

QMC5883LCompass compass;

void setup() {
	Wire.setPins(15,27);
  Wire.begin();        // Inicia I2C (necesario en ESP32 aunque no se especifiquen pines aquí)
  Wire.setClock(400000); // Opcional: 400 kHz
  
  Serial.begin(115200); // Baudrate más alto para ESP32
  compass.init();
  compass.setCalibrationOffsets(-542.00, -416.00, -78.00);
  compass.setCalibrationScales(1.01, 0.99, 1.00);
}

void loop() {
  int x, y, z, a, b;
  char myArray[3];
  
  compass.read();
  
  x = compass.getX();
  y = compass.getY();
  z = compass.getZ();
  
  a = -90 - compass.getAzimuth();
  if (a < 0) {
    a = 360 + a;
  }
  
  b = compass.getBearing(a);
  compass.getDirection(myArray, a);
  
  Serial.print("X: "); Serial.print(x);
  Serial.print(" Y: "); Serial.print(y);
  Serial.print(" Z: "); Serial.print(z);
  Serial.print(" Azimuth: "); Serial.print(a);
  Serial.print(" Bearing: "); Serial.print(b);
  Serial.print(" Direction: "); 
  Serial.print(myArray[0]); Serial.print(myArray[1]); Serial.print(myArray[2]);
  Serial.println();
  
  delay(250);
}