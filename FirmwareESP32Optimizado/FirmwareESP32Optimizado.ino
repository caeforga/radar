#include <FastAccelStepper.h>
#include <QMC5883LCompass.h>
#include <Wire.h>
#include <HardwareSerial.h>

// Definición de botones (sin cambios)
#define VP 23
#define RNG_ARRIBA 22  
#define RNG_ABAJO 21 
#define TRK_IZQUIERDA 19   
#define TRK_DERECHA 18    

// Selector (sin cambios)
#define PIN2 5
#define PIN8 17
#define PIN9 16

// Motores - cambiamos a FastAccelStepper
#define stepPin1 32  // Nota: FastAccelStepper usa solo el pin STEP
#define dirPin1 33
#define stepPin2 27
#define dirPin2 14


// GPS - Brujula
#define SDA_pin 4
#define SCL_pin 2


// Objeto brujula
QMC5883LCompass compass;
TaskHandle_t Task1;
String GGA="";
String RMC="";
unsigned long treferencia=0;

//Serial 2 para el gps

HardwareSerial serial2(2);
#define serial2RX 15
#define serial2TX 13



// Objetos FastAccelStepper
FastAccelStepperEngine engine;
FastAccelStepper *stepper1;
FastAccelStepper *stepper2;

float proxPosition1 = 0;
float proxPosition2 = 0;

// Potenciómetros (sin cambios)
const int GAIN = DAC1;  // gpio 25
int raw = 0;
const int TILT = DAC2;  // gpio 26
int raw2 = 125;

bool estadoVP = HIGH;
bool estadoRNG_ARRIBA = HIGH;
bool estadoRNG_ABAJO = HIGH;
bool estadoTRK_IZQUIERDA = HIGH;
bool estadoTRK_DERECHA = HIGH;


void setup() {
  // Configuración de pines digitales (sin cambios)
  pinMode(VP, OUTPUT); 
  pinMode(RNG_ARRIBA, OUTPUT); 
  pinMode(RNG_ABAJO, OUTPUT); 
  pinMode(TRK_IZQUIERDA, OUTPUT); 
  pinMode(TRK_DERECHA, OUTPUT);

  digitalWrite(VP, estadoVP);
  digitalWrite(RNG_ARRIBA, estadoRNG_ARRIBA);  
  digitalWrite(RNG_ABAJO, estadoRNG_ABAJO);  
  digitalWrite(TRK_IZQUIERDA, estadoTRK_IZQUIERDA);  
  digitalWrite(TRK_DERECHA, estadoTRK_DERECHA);

  Serial.begin(115200);
  dacWrite(GAIN, raw);
  dacWrite(TILT, raw2);

  serial2.begin(9600,SERIAL_8N1,serial2RX,serial2TX);

  // Selector (sin cambios)
  pinMode(PIN2, OUTPUT);
  pinMode(PIN8, OUTPUT);
  pinMode(PIN9, OUTPUT);
  digitalWrite(PIN2, HIGH);
  digitalWrite(PIN8, HIGH);
  digitalWrite(PIN9, HIGH);

  // Configuración de motores con FastAccelStepper
  engine.init();
  stepper1 = engine.stepperConnectToPin(stepPin1);
  stepper1->setDirectionPin(dirPin1);
  stepper1->setSpeedInHz(400);        // Equivalente a setMaxSpeed(100)
  stepper1->setAcceleration(400);     // Mismo valor que antes
  
  stepper2 = engine.stepperConnectToPin(stepPin2);
  stepper2->setDirectionPin(dirPin2);
  stepper2->setSpeedInHz(800);        // Equivalente a setMaxSpeed(800)
  stepper2->setAcceleration(200);     // Mismo valor que antes

  // Configuracion I2C
  Wire.setPins(SDA_pin,SCL_pin);
  Wire.begin();        // Inicia I2C (necesario en ESP32 aunque no se especifiquen pines aquí)
  Wire.setClock(400000); // Opcional: 400 kHz

  //Configuracion Brujula
  compass.init();
  compass.setCalibrationOffsets(-542.00, -416.00, -78.00);
  compass.setCalibrationScales(1.01, 0.99, 1.00);


  xTaskCreatePinnedToCore(
    loop2,
    "Task_1",
    4096,
    NULL,
    1,
    &Task1,
    0
  );
}


void loop() {
  // Verificar si hay datos disponibles en el puerto serial (sin cambios)
  if (Serial.available() > 0) {
    String entrada = Serial.readStringUntil('\n');
    entrada.trim();
    char primerCaracter = entrada.charAt(0);
    

    //Confirmacion conexion establecida y datos brujula

    if (primerCaracter == 'I'){
      Serial.print("1");  
    }



    // Potenciómetros (sin cambios)
    if (primerCaracter == 'G') {
      String numeroStr = entrada.substring(1);
      int newRaw = numeroStr.toInt();
      if (newRaw >= 0 && newRaw <= 31) {
        if (newRaw == 0){
          raw = 0;
        } else if(newRaw == 31){
          raw = 255;
        } else{
          raw = (newRaw-0.4426)/0.1193;
        }
        dacWrite(GAIN, raw);
      }
      Serial.print(raw);
    } else if (primerCaracter == 'T') {
      String numeroStr2 = entrada.substring(2);
      float newRaw2 = numeroStr2.toFloat();
      char tiltUpDown = entrada.charAt(1);
      if (tiltUpDown == 'D'){
        Serial.println("Entro en la D");
        raw2=(newRaw2-15.245)/(-0.1209);
        Serial.println(raw2);
      } else if (tiltUpDown == 'U'){
        Serial.println("Entro en la U");
        raw2=(newRaw2+14.965)/0.1198;
        Serial.println(raw2);
      }
      if (raw2 >= 0 && raw2 <= 255) {
        dacWrite(TILT, raw2);
      }
      Serial.print(raw2);
    } else if (primerCaracter == 'M'){
      int posComa = entrada.indexOf(',');
      if (posComa > 0) {
        proxPosition1 = entrada.substring(1, posComa).toFloat() * 1600 / 360.0 * 20;
        proxPosition2 = entrada.substring(posComa + 1).toFloat() * 1600 / 360.0 * 6;
        Serial.println(proxPosition1);

        // Detener motores (adaptado para FastAccelStepper)
        stepper1->stopMove();
        stepper2->stopMove();

        // Mover a nuevas posiciones
        stepper1->moveTo((int)proxPosition1);
        stepper2->moveTo((int)proxPosition2);
      }
    }

    // Botones (sin cambios)
    if (entrada == "vp") {
      digitalWrite(VP, LOW);
      delay(200);
      digitalWrite(VP, HIGH);
    } else if (entrada == "rng_arriba") {
      digitalWrite(RNG_ARRIBA, LOW);
      delay(200);
      digitalWrite(RNG_ARRIBA, HIGH);
    } else if (entrada == "rng_abajo") {
      digitalWrite(RNG_ABAJO, LOW);
      delay(200);
      digitalWrite(RNG_ABAJO, HIGH);
    } else if (entrada == "trk_izquierda") {
      digitalWrite(TRK_IZQUIERDA, LOW);
      delay(200);
      digitalWrite(TRK_IZQUIERDA, HIGH);
    } else if (entrada == "trk_derecha") {
      digitalWrite(TRK_DERECHA, LOW);
      delay(200);
      digitalWrite(TRK_DERECHA, HIGH);
    }

    // Selectores (sin cambios)
    if (entrada == "sby") {
      digitalWrite(PIN2, LOW);
      digitalWrite(PIN8, LOW);
      digitalWrite(PIN9, HIGH);
      Serial.println("Modo SBY.");
    } else if (entrada == "tst") {
      digitalWrite(PIN2, LOW);
      digitalWrite(PIN8, HIGH);
      digitalWrite(PIN9, LOW);
      Serial.println("Modo TST");
    } else if (entrada == "on"){
      digitalWrite(PIN2, LOW);
      digitalWrite(PIN8, HIGH);
      digitalWrite(PIN9, HIGH);
      Serial.println("Modo ON");
    } else if (entrada == "off"){
      digitalWrite(PIN2, HIGH);
      digitalWrite(PIN8, HIGH);
      digitalWrite(PIN9, HIGH);
      Serial.println("Modo OFF");
    } 

    while (Serial.available()) Serial.read();
  }

}

void loop2(void *parameter){
  delay(1000);
  

  while(1){
    compass.read();
    int a = -90-compass.getAzimuth();
    if(a<0){
      a=360+a;
    }
    while(serial2.available() > 0){
      String aux= serial2.readStringUntil('\n');
      if(aux.startsWith("$GNGGA") || aux.startsWith("$GPGGA")){
        GGA=aux;
      }else if (aux.startsWith("$GNRMC") || aux.startsWith("$GPRMC")){
        RMC=aux;
      }
    }
    if (millis() - treferencia >= 10000){
      if (GGA.length() >0){
        Serial.println(GGA);
      }
      if (RMC.length() >0){
        Serial.println(RMC);
      }
      Serial.println(a);
      treferencia=millis();    
    }
    delay(500);
  
  }

}