# Blood-group-project
## Connections 

```
R307S Fingerprint Sensor ↔ ESP32
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VCC (Red)     →  3.3V
GND (Black)   →  GND
TX (Green)    →  GPIO 16 (RX2)
RX (White)    →  GPIO 17 (TX2)
```

## Verification kosam

```
#include <Adafruit_Fingerprint.h>

HardwareSerial mySerial(2);
Adafruit_Fingerprint finger = Adafruit_Fingerprint(&mySerial);




void setup() {
  Serial.begin(115200);
  mySerial.begin(57600, SERIAL_8N1, 16, 17);
  
  delay(1000);
  
  Serial.println("\n\nFingerprint Sensor Test");
  
  if (finger.verifyPassword()) {
    Serial.println("Sensor dorikindi!");
  } else {
    Serial.println("Sensor dorukaledu!");
    while (1) { delay(1); }
  }
  
  
  Serial.println("Chethi sensor meeda pettu...");
}

void loop() {
  uint8_t p = finger.getImage();
  
  if (p == FINGERPRINT_OK) {
    Serial.println("Image teesukunna!");
    
    p = finger.image2Tz();
    if (p == FINGERPRINT_OK) {
      Serial.println("Image template aipoindi");
      Serial.println("-----");
      delay(2000);
    }
  }
  delay(50);
}
```
