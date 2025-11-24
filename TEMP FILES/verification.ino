#include <Adafruit_Fingerprint.h>

HardwareSerial mySerial(2);
Adafruit_Fingerprint finger = Adafruit_Fingerprint(&mySerial);




void setup() {
  Serial.begin(115200);
  while (!Serial);

  Serial.println("\n\n=== Fingerprint Sensor Diagnostic ===");

  mySerial.begin(57600, SERIAL_8N1, 16, 17);
  delay(100);

  Serial.println("Sensor tho matladatam chustunnan...");

  uint8_t status = finger.verifyPassword();
  if (status == FINGERPRINT_OK) {
    Serial.println("Sensor dorikindi, password sari!");
  } else {
    Serial.print("Sensor lo problem, code: 0x");
    Serial.println(status, HEX);
    Serial.println("Wiring chuskoo, 5V isthunnav aa?, baud rate sari aa?");
    Serial.println("Nillipoyan...");
    while (1) {
      delay(1000);
    }
  }

  Serial.println("Ready. Finger sensor meeda pettu.");
}

void loop() {
  Serial.println("Finger kosam wait chestunnan...");

  uint8_t p = finger.getImage();
  if (p == FINGERPRINT_OK) {
    Serial.println("Photo teesukunna!");
    
    p = finger.image2Tz();
    if (p == FINGERPRINT_OK) {
      Serial.println("Template sari aipoindi.");
    } else {
      Serial.print("Template lo problem, code: 0x");
      Serial.println(p, HEX);
    }
  } else if (p == FINGERPRINT_NOFINGER) {
  } else {
    Serial.print("Photo teesukovala, code: 0x");
    Serial.println(p, HEX);
  }

  delay(1000);
}
