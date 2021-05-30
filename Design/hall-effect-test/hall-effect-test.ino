int hallSensorPin = 2;      
int newState;          
int oldState;

unsigned long startTime;  // unsigned means only +ve numbers
unsigned long endTime;    // unsigned long is the datatype required for storing times.

bool firstPass = true;    // used to differentiate between the two sensor activations

          
void setup() {     
  pinMode(hallSensorPin, INPUT); // setup the pins
  Serial.begin(9600);            // setup the serial port
}

void loop(){
  // read from the sensor
  newState = digitalRead(hallSensorPin);

// check for a change of state
  if ((newState == 0) and (oldState == 1)) {
    if (firstPass) {
      startTime = millis(); 
      firstPass = false;
    } 
    else {
      endTime = millis();
      Serial.println(String(hallSensorPin, DEC)+" "+ String(endTime-startTime, DEC));
      firstPass = true;
    }
  }
  oldState = newState;
}
