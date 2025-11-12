#include <AccelStepper.h>

//se definen los botones
#define VP 2  // Define botón
#define RNG_ARRIBA 4  
#define RNG_ABAJO 5 
#define TRK_IZQUIERDA 18   
#define TRK_DERECHA 19    


//selector
#define PIN2 12
#define PIN8 13
#define PIN9 14


//motores
#define dirPin1 32
#define stepPin1 33
#define motorInterfaceType1 1

#define dirPin2 21
#define stepPin2 22
#define motorInterfaceType2 1

AccelStepper stepper1 = AccelStepper(motorInterfaceType1, stepPin1, dirPin1);
AccelStepper stepper2 = AccelStepper(motorInterfaceType2, stepPin2, dirPin2);
float proxPosition1 = 0;
float proxPosition2 = 0;



//se definen los potenciometros
const int GAIN = DAC1;//gpio 25
int raw = 0;
const int TILT = DAC2;//gpio 26
int raw2 = 125;

bool estadoVP = HIGH;
bool estadoRNG_ARRIBA = HIGH;
bool estadoRNG_ABAJO = HIGH;
bool estadoTRK_IZQUIERDA = HIGH;
bool estadoTRK_DERECHA = HIGH;


void setup() {
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


  pinMode(PIN2, OUTPUT); // Configura el pin como salida
  pinMode(PIN8, OUTPUT);
  pinMode(PIN9, OUTPUT);

  digitalWrite(PIN2, LOW); // Inicializa el pin en LOW
  digitalWrite(PIN8, LOW);
  digitalWrite(PIN9, LOW);



  stepper1.setMaxSpeed(100);
  stepper1.setAcceleration(100);


  stepper2.setMaxSpeed(800);
  stepper2.setAcceleration(200);

}

void loop() {
  // Verificar si hay datos disponibles en el puerto serial
  if (Serial.available() > 0) {
    String entrada = Serial.readStringUntil('\n');
    entrada.trim(); // Elimina espacios o saltos de línea
    char primerCaracter = entrada.charAt(0); // Obtener el último carácter



    //Este if es para los potenciometros
    if (primerCaracter == 'G') {
      //AQUI VA LA RUTINA DE GAIN
      String numeroStr = entrada.substring(1); // Obtener el resto de la cadena
      int newRaw = numeroStr.toInt(); // Convertir el número a entero
      if (newRaw >= 0 && newRaw <= 31) { // Validar el rango
        if (newRaw == 0){
          raw = 0;
        } else if(newRaw == 31){
          raw = 255;
        } else{
          raw = (newRaw-0.4426)/0.1193;
        }
        dacWrite(GAIN, raw); // Escribir el nuevo valor en el DAC
      }
      Serial.print(raw);
      } else if (primerCaracter == 'T') {
        //AQUI VA LA RUTINA DE TILT
        String numeroStr2 = entrada.substring(2); // Obtener el resto de la cadena
        float newRaw2 = numeroStr2.toFloat(); // Convertir el número a entero
        char tiltUpDown = entrada.charAt(1); // Obtener el segundo carácter
        if (tiltUpDown == 'D'){
          Serial.println("Entro en la D");
          raw2=(newRaw2-15.245)/(-0.1209);
          Serial.println(raw2);
        } else if (tiltUpDown == 'U'){
          Serial.println("Entro en la U");
          raw2=(newRaw2+14.965)/0.1198;
          Serial.println(raw2);
        }
        if (newRaw2 >= 0 && newRaw2 <= 255) { // Validar el rango
          //raw2 = newRaw2;
          dacWrite(TILT, raw2); // Escribir el nuevo valor en el DAC
      }
      Serial.print(raw2);
      } else if (primerCaracter == 'M'){
          int posComa = entrada.indexOf(',');

        if (posComa > 0) {
          // Convertir los datos recibidos a las nuevas posiciones
          proxPosition1 = entrada.substring(1, posComa).toFloat() * 400 / 360.0 * 5.125;
          proxPosition2 = entrada.substring(posComa + 1).toFloat() * 1600 / 360.0 * 6;
          Serial.println(proxPosition1);

          // Detener motores suavemente antes de actualizar posiciones
          stepper1.stop();
          stepper2.stop();

          // Mover a nuevas posiciones
          stepper1.moveTo((int)proxPosition1);
          stepper2.moveTo((int)proxPosition2);
        }
        // Continuamente actualizar los motores
        //stepper1.run();
        //stepper2.run();
      }//if (primerCaracter == 'T')
      


      //AQUI ESTAN LOS BOTONES
      if (entrada == "vp") {
        digitalWrite(VP, LOW); // Activa el pin (cambia a LOW si era HIGH)
        delay(200);           // Espera
        digitalWrite(VP, HIGH); // Vuelve al estado inicial
      } 
      else if (entrada == "rng_arriba") {
        digitalWrite(RNG_ARRIBA, LOW);
        delay(200);
        digitalWrite(RNG_ARRIBA, HIGH);
      } 
      else if (entrada == "rng_abajo") {
        digitalWrite(RNG_ABAJO, LOW);
        delay(200);
        digitalWrite(RNG_ABAJO, HIGH);
      } 
      else if (entrada == "trk_izquierda") {
        digitalWrite(TRK_IZQUIERDA, LOW);
        delay(200);
        digitalWrite(TRK_IZQUIERDA, HIGH);
      } 
      else if (entrada == "trk_derecha") {
        digitalWrite(TRK_DERECHA, LOW);
        delay(200);
        digitalWrite(TRK_DERECHA, HIGH);
      }

      //AQUI VAN LOS SELECTORES
      if (entrada == "sby") {
        digitalWrite(PIN2, HIGH);
        digitalWrite(PIN8, HIGH);
        digitalWrite(PIN9, LOW);
        //digitalWrite(PIN11, LOW);
        Serial.println("Modo SBY.");
      } else if (entrada == "tst") {
        digitalWrite(PIN2, HIGH);
        digitalWrite(PIN8, LOW);
        digitalWrite(PIN9, HIGH);
        //digitalWrite(PIN11, LOW);
        Serial.println("Modo TST");
      } else if (entrada == "on"){
        digitalWrite(PIN2, HIGH);
        digitalWrite(PIN8, LOW);
        digitalWrite(PIN9, LOW);
        //digitalWrite(PIN11, LOW);
        Serial.println("Modo ON");
      } else if (entrada == "off"){
        digitalWrite(PIN2, LOW);
        digitalWrite(PIN8, LOW);
        digitalWrite(PIN9, LOW);
        //digitalWrite(PIN11, LOW);
        Serial.println("Modo OFF");
      } 

    while (Serial.available()) Serial.read(); // Limpiar buffer

  }//if serial
  stepper1.run();
  stepper2.run();
}