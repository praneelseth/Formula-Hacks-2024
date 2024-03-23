#include <Servo.h>

// Define the servo pin and the analog input pin
#define SERVO_PIN 1
#define ANALOG_PIN A1
#define WRITE_PIN 9

// Define the threshold value
#define THRESHOLD 500

// Define the maximum and minimum servo angles
#define MAX_ANGLE 90
#define MIN_ANGLE 0

// Create a servo object
Servo myServo;

// Variables to control the servo movement
int servoAngle = MIN_ANGLE; // Current angle of the servo
bool increasing = true;     // Whether the servo angle is increasing or decreasing

void setup() {
  // Initialize the servo
  myServo.attach(SERVO_PIN);
  
  // Initialize serial communication at 9600 bits per second
  Serial.begin(9600);

  pinMode(WRITE_PIN, OUTPUT);
}

void loop() {
  // Read the value from the analog pin
  int sensorValue = analogRead(ANALOG_PIN);
  Serial.println(sensorValue); // Print the sensor value to the serial monitor
  
  // Check if the sensor value exceeds the threshold
  if (sensorValue>THRESHOLD) {
    digitalWrite(WRITE_PIN, HIGH);
    // If it does, move the servo
    if (increasing) {
      servoAngle+=15;
      if (servoAngle >= MAX_ANGLE) {
        increasing = false; // Change direction to decreasing once the max angle is reached
      }
    } else {
      servoAngle-=15;
      if (servoAngle <= MIN_ANGLE) {
        increasing = true; // Change direction to increasing once the min angle is reached
      }
    }
    if (increasing) {
      myServo.write(90); // Update the servo to the new angle
    } else {
      myServo.write(0); // Update the servo to the new angle
    }
  } else {
    // If it doesn't exceed the threshold, reset the servo to 0 degrees
    digitalWrite(WRITE_PIN, LOW);
    servoAngle = MIN_ANGLE; // Reset the angle if the condition is not met
    myServo.write(servoAngle);
  }
  
  // Wait for a moment before reading again to make movement visible
  delay(500); // Adjust this delay for smoother or faster servo movement
}
