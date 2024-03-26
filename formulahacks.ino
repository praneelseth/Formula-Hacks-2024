/*
  Blink

  Turns an LED on for one second, then off for one second, repeatedly.

  Most Arduinos have an on-board LED you can control. On the UNO, MEGA and ZERO
  it is attached to digital pin 13, on MKR1000 on pin 6. LED_BUILTIN is set to
  the correct LED pin independent of which board is used.
  If you want to know what pin the on-board LED is connected to on your Arduino
  model, check the Technical Specs of your board at:
  https://www.arduino.cc/en/Main/Products

  modified 8 May 2014
  by Scott Fitzgerald
  modified 2 Sep 2016
  by Arturo Guadalupi
  modified 8 Sep 2016
  by Colby Newman

  This example code is in the public domain.

  https://www.arduino.cc/en/Tutorial/BuiltInExamples/Blink
*/


const int SHT_PIN = 2;

const int T_PIN = 3;
unsigned long shootPreviousTime = 0;
unsigned long tPreviousTime = 0;

const int moveDuration = 1000; // 200ms


// the setup function runs once when you press reset or power the board
void setup() {
  
  // initialize digital pin LED_BUILTIN as an output.
  pinMode(19, INPUT_PULLUP);
  
  pinMode(SHT_PIN, OUTPUT);
    pinMode(T_PIN, OUTPUT);

  digitalWrite(SHT_PIN, LOW);
    digitalWrite(T_PIN, LOW);

  Serial.begin(9600);
  Serial.println("HIHIHIHI");
  
}

// the loop function runs over and over again forever
void loop() {
  if (Serial.available() > 0) {
    char command = Serial.read(); // Read the incoming command

    if ( command == 'S') {
      digitalWrite(SHT_PIN, HIGH);
      shootPreviousTime = millis();
    }
    if ( command == 'T') {
      digitalWrite(T_PIN, HIGH);
      shootPreviousTime = millis();
    }

  }


  if (shootPreviousTime < ( millis() - moveDuration)) {
    digitalWrite(SHT_PIN, LOW);
  }
  
  if (tPreviousTime < ( millis() - 200)) {
    digitalWrite(T_PIN, LOW);
  }
if (!digitalRead(19)) {
  Serial.println("P");

}

 
}
