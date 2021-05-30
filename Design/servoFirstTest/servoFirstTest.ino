#include <Servo.h>

Servo servo;
int angle;

void setup() {
  Serial.begin(9600);
  servo.attach(9);
}

void loop() {
  // check if there is any data to read
  if (Serial.available() > 0) {
    // read the incoming byte:
    angle = Serial.read();
    servo.write(angle);
  }
}
