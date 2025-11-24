// File: quick_demo_system.ino

/*
 * ═══════════════════════════════════════════════════════════════
 * QUICK DEMO - COMPLETE FINGERPRINT BLOOD GROUP DETECTION
 * ═══════════════════════════════════════════════════════════════
 * 
 * JUST PLACE FINGER → GET BLOOD GROUP INSTANTLY!
 * 
 * Auto-enrolls if finger is new
 * Auto-predicts if finger is enrolled
 */

#include <HardwareSerial.h>

HardwareSerial mySerial(2);

#define RX_PIN 16
#define TX_PIN 17

uint8_t nextID = 1;

void setup() {
  Serial.begin(115200);
  delay(2000);
  
  Serial.println("\n\n");
  Serial.println("╔═══════════════════════════════════════════════════════╗");
  Serial.println("║  FINGERPRINT BLOOD GROUP DETECTION - QUICK DEMO      ║");
  Serial.println("║  >>> PLACE FINGER TO GET BLOOD GROUP <<<             ║");
  Serial.println("╚═══════════════════════════════════════════════════════╝");
  Serial.println();
  
  mySerial.begin(57600, SERIAL_8N1, RX_PIN, TX_PIN);
  delay(500);
  
  Serial.println("✅ System ready!");
  Serial.println("✅ Python server should be running");
  Serial.println();
  Serial.println("═══════════════════════════════════════════════════════");
  Serial.println(">>> PLACE YOUR FINGER ON THE SENSOR <<<");
  Serial.println("═══════════════════════════════════════════════════════");
  Serial.println();
}

void loop() {
  // Wait for finger
  if (getImage() == 0) {
    Serial.println("\n🖐️  FINGER DETECTED!");
    Serial.println("→ Processing...");
    
    delay(200);
    
    // Convert to template
    if (image2Tz(1) == 0) {
      Serial.println("✅ Fingerprint captured");
      
      // Try to search for match
      int fingerID = searchFingerprint();
      
      if (fingerID >= 0) {
        Serial.print("✅ Recognized finger ID #");
        Serial.println(fingerID);
      } else {
        Serial.println("→ New finger detected - Auto-enrolling...");
        
        if (quickEnroll()) {
          Serial.print("✅ Enrolled as ID #");
          Serial.println(nextID - 1);
        } else {
          Serial.println("⚠️  Enrollment skipped");
        }
      }
      
      // Now predict blood group
      Serial.println("\n🔮 DETECTING BLOOD GROUP...");
      Serial.println("PREDICT_NOW");
      
      // Wait for Python response
      unsigned long start = millis();
      String response = "";
      
      while (millis() - start < 5000) {
        if (Serial.available()) {
          char c = Serial.read();
          if (c == '\n') {
            if (response.startsWith("BLOOD_GROUP:")) {
              String bloodGroup = response.substring(12);
              bloodGroup.trim();
              
              Serial.println("\n╔═══════════════════════════════════════════════════╗");
              Serial.println("║           🩸 BLOOD GROUP RESULT 🩸                ║");
              Serial.println("╚═══════════════════════════════════════════════════╝");
              Serial.println();
              Serial.print("         >>> YOUR BLOOD GROUP: ");
              Serial.print(bloodGroup);
              Serial.println(" <<<");
              Serial.println();
              Serial.println("╚═══════════════════════════════════════════════════╝");
              Serial.println();
              
              break;
            }
            response = "";
          } else {
            response += c;
          }
        }
        delay(10);
      }
      
      Serial.println("\n═══════════════════════════════════════════════════════");
      Serial.println(">>> PLACE FINGER AGAIN FOR ANOTHER TEST <<<");
      Serial.println("═══════════════════════════════════════════════════════\n");
      
      // Wait for finger removal
      delay(2000);
      while (getImage() == 0) {
        delay(100);
      }
      delay(1000);
    }
  }
  
  delay(50);
}

bool quickEnroll() {
  Serial.println("   → Remove finger...");
  delay(2000);
  
  while (getImage() == 0) delay(50);
  
  Serial.println("   → Place same finger again...");
  
  int attempts = 0;
  while (getImage() != 0 && attempts < 100) {
    delay(50);
    attempts++;
  }
  
  if (attempts >= 100) {
    return false;
  }
  
  delay(200);
  
  if (image2Tz(2) != 0) {
    return false;
  }
  
  if (createModel() != 0) {
    return false;
  }
  
  if (storeModel(nextID) != 0) {
    return false;
  }
  
  nextID++;
  return true;
}

int searchFingerprint() {
  uint8_t packet[] = {0xEF, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x01, 0x00, 0x08, 0x04, 0x01, 0x00, 0x00, 0x00, 0xC8, 0x00, 0xD6};
  
  while (mySerial.available()) mySerial.read();
  mySerial.write(packet, sizeof(packet));
  delay(300);
  
  if (mySerial.available() >= 16) {
    uint8_t response[16];
    for (int i = 0; i < 16; i++) {
      response[i] = mySerial.read();
    }
    
    if (response[0] == 0xEF && response[1] == 0x01) {
      if (response[9] == 0x00) {
        return (response[10] << 8) | response[11];
      }
    }
  }
  
  return -1;
}

int getImage() {
  uint8_t packet[] = {0xEF, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x01, 0x00, 0x03, 0x01, 0x00, 0x05};
  
  while (mySerial.available()) mySerial.read();
  mySerial.write(packet, sizeof(packet));
  delay(100);
  
  if (mySerial.available() >= 12) {
    uint8_t response[12];
    for (int i = 0; i < 12; i++) {
      response[i] = mySerial.read();
    }
    
    if (response[0] == 0xEF && response[1] == 0x01) {
      if (response[9] == 0x00) return 0;
      if (response[9] == 0x02) return -2;
    }
  }
  
  return -1;
}

int image2Tz(uint8_t slot) {
  uint8_t packet[] = {0xEF, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x01, 0x00, 0x04, 0x02, slot, 0x00, 0x00};
  
  uint16_t sum = 0x02 + slot + 0x01 + 0x00 + 0x04;
  packet[11] = (sum >> 8) & 0xFF;
  packet[12] = sum & 0xFF;
  
  while (mySerial.available()) mySerial.read();
  mySerial.write(packet, sizeof(packet));
  delay(300);
  
  if (mySerial.available() >= 12) {
    uint8_t response[12];
    for (int i = 0; i < 12; i++) {
      response[i] = mySerial.read();
    }
    
    if (response[0] == 0xEF && response[1] == 0x01) {
      return response[9];
    }
  }
  
  return -1;
}

int createModel() {
  uint8_t packet[] = {0xEF, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x01, 0x00, 0x03, 0x05, 0x00, 0x09};
  
  while (mySerial.available()) mySerial.read();
  mySerial.write(packet, sizeof(packet));
  delay(300);
  
  if (mySerial.available() >= 12) {
    uint8_t response[12];
    for (int i = 0; i < 12; i++) {
      response[i] = mySerial.read();
    }
    
    if (response[0] == 0xEF && response[1] == 0x01) {
      return response[9];
    }
  }
  
  return -1;
}

int storeModel(uint8_t id) {
  uint8_t packet[] = {0xEF, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x01, 0x00, 0x06, 0x06, 0x01, 0x00, id, 0x00, 0x00};
  
  uint16_t sum = 0x01 + 0x00 + 0x06 + 0x06 + 0x01 + 0x00 + id;
  packet[13] = (sum >> 8) & 0xFF;
  packet[14] = sum & 0xFF;
  
  while (mySerial.available()) mySerial.read();
  mySerial.write(packet, sizeof(packet));
  delay(300);
  
  if (mySerial.available() >= 12) {
    uint8_t response[12];
    for (int i = 0; i < 12; i++) {
      response[i] = mySerial.read();
    }
    
    if (response[0] == 0xEF && response[1] == 0x01) {
      return response[9];
    }
  }
  
  return -1;
}

// File: quick_demo_system.ino