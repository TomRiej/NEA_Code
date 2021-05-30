

class HallEffectSensor {
  private:
    byte pinNumber;
    byte newState;
    byte oldState;
    unsigned long startTime;
    unsigned long endTime;
    bool firstPass; 
  
  public:
    HallEffectSensor() {    // Constructor
      firstPass = true;     // no parameters for the constructor
    }
    
    void setPinNumber(byte pin){
      pinNumber = pin;
      pinMode(pinNumber, INPUT);
    }

    void readPin() {
      newState = digitalRead(pinNumber);
      
      if ((newState == LOW) and (oldState == HIGH)) { // LOW == 0, HIGH == 1
        if (firstPass) {
          startTime = millis(); 
          firstPass = false;
        } 
        else {
          endTime = millis();
          Serial.println(String(pinNumber, DEC)+" "+String(endTime - startTime, DEC)); 
          firstPass = true;
        }
      }
      oldState = newState;
    }
    
    
};


const int numSensors = 4;
const int pins[numSensors] = {2, 3, 4, 5}; // the physical pin numbers each sensor is attached to

HallEffectSensor sensors[numSensors]; // in order to define an empty array of objects,
                                      // the contructor for the object must have 0 parameters


void setup() {
  Serial.begin(9600);                 // setup the serial port   

  for (int i=0; i<numSensors; i++){
    sensors[i] = HallEffectSensor();  // initialising each object 
    sensors[i].setPinNumber(pins[i]); // and assigning them their own pin
  }
  
  
}

void loop(){
  for (int i=0;i<numSensors;i++){
    sensors[i].readPin();
  }
  
}



// Interupts only work on pins 2 and 3
