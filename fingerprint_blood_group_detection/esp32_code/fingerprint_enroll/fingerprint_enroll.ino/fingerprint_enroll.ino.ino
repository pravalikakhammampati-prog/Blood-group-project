// File: esp32_code/fingerprint_enroll/fingerprint_enroll.ino

/*
 * ═══════════════════════════════════════════════════════════════
 * PHASE 2 - STEP 2.2: R307 FINGERPRINT ENROLLMENT
 * ═══════════════════════════════════════════════════════════════
 * 
 * This sketch enrolls fingerprints into the R307 sensor
 * You need to scan the same finger twice for enrollment
 */

#include <HardwareSerial.h>

HardwareSerial mySerial(2);

#define RX_PIN 16
#define TX_PIN 17

uint8_t fingerID = 0;

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n\n");
  Serial.println("╔════════════════════════════════════════════════╗");
  Serial.println("║   R307 FINGERPRINT ENROLLMENT SYSTEM           ║");
  Serial.println("║   PHASE 2 - STEP 2.2                          ║");
  Serial.println("╚════════════════════════════════════════════════╝");
  Serial.println();
  
  mySerial.begin(57600, SERIAL_8N1, RX_PIN, TX_PIN);
  delay(500);
  
  Serial.println("Ready to enroll fingerprints!");
  Serial.println("Each person should enroll at least one finger.");
  Serial.println();
}

void loop() {
  Serial.println("\n════════════════════════════════════════════════");
  Serial.println("Enter fingerprint ID to enroll (0-255):");
  Serial.println("(Each person gets a unique ID)");
  Serial.println("════════════════════════════════════════════════");
  
  while (!Serial.available()) {
    delay(100);
  }
  
  fingerID = Serial.parseInt();
  
  // Clear buffer
  while (Serial.available()) {
    Serial.read();
  }
  
  Serial.print("\n→ Enrolling fingerprint ID #");
  Serial.println(fingerID);
  
  if (enrollFingerprint(fingerID)) {
    Serial.println("\n✅ ENROLLMENT SUCCESSFUL!");
    Serial.print("✅ Fingerprint ID #");
    Serial.print(fingerID);
    Serial.println(" saved to sensor");
  } else {
    Serial.println("\n❌ ENROLLMENT FAILED!");
    Serial.println("⚠️  Please try again");
  }
  
  delay(2000);
}

bool enrollFingerprint(uint8_t id) {
  int p = -1;
  
  // Step 1: Get first image
  Serial.println("\n→ Place finger on sensor...");
  while (p != 0) {
    p = getImage();
    if (p == -1) {
      Serial.println("❌ Communication error");
      return false;
    }
    delay(100);
  }
  Serial.println("✅ Image captured");
  
  // Step 2: Convert first image to characteristics
  p = image2Tz(1);
  if (p != 0) {
    Serial.println("❌ Failed to convert image");
    return false;
  }
  Serial.println("✅ Image converted");
  
  // Step 3: Get second image
  Serial.println("\n→ Remove finger");
  delay(2000);
  
  p = 0;
  Serial.println("→ Place SAME finger again...");
  while (p != 0) {
    p = getImage();
    if (p == -1) {
      Serial.println("❌ Communication error");
      return false;
    }
    delay(100);
  }
  Serial.println("✅ Second image captured");
  
  // Step 4: Convert second image
  p = image2Tz(2);
  if (p != 0) {
    Serial.println("❌ Failed to convert second image");
    return false;
  }
  Serial.println("✅ Second image converted");
  
  // Step 5: Create model
  Serial.println("\n→ Creating fingerprint model...");
  p = createModel();
  if (p != 0) {
    Serial.println("❌ Failed to create model");
    Serial.println("⚠️  Fingers did not match");
    return false;
  }
  Serial.println("✅ Model created");
  
  // Step 6: Store model
  Serial.print("→ Storing model in ID #");
  Serial.println(id);
  p = storeModel(id);
  if (p != 0) {
    Serial.println("❌ Failed to store model");
    return false;
  }
  Serial.println("✅ Model stored");
  
  return true;
}

int getImage() {
  // GenImg command
  uint8_t packet[] = {0xEF, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x01, 0x00, 0x03, 0x01, 0x00, 0x05};
  
  while (mySerial.available()) mySerial.read();
  mySerial.write(packet, sizeof(packet));
  delay(200);
  
  if (mySerial.available() >= 12) {
    uint8_t response[12];
    for (int i = 0; i < 12; i++) {
      response[i] = mySerial.read();
    }
    
    if (response[0] == 0xEF && response[1] == 0x01) {
      if (response[9] == 0x00) return 0; // Success
      if (response[9] == 0x02) return -2; // No finger
    }
  }
  
  return -1; // Error
}

int image2Tz(uint8_t slot) {
  // Img2Tz command
  uint8_t packet[] = {0xEF, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x01, 0x00, 0x04, 0x02, slot, 0x00, 0x00};
  
  // Calculate checksum
  uint16_t sum = 0x02 + slot + 0x01 + 0x00 + 0x04;
  packet[11] = (sum >> 8) & 0xFF;
  packet[12] = sum & 0xFF;
  
  while (mySerial.available()) mySerial.read();
  mySerial.write(packet, sizeof(packet));
  delay(500);
  
  if (mySerial.available() >= 12) {
    uint8_t response[12];
    for (int i = 0; i < 12; i++) {
      response[i] = mySerial.read();
    }
    
    if (response[0] == 0xEF && response[1] == 0x01) {
      return response[9]; // 0 = success
    }
  }
  
  return -1;
}

int createModel() {
  // RegModel command
  uint8_t packet[] = {0xEF, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x01, 0x00, 0x03, 0x05, 0x00, 0x09};
  
  while (mySerial.available()) mySerial.read();
  mySerial.write(packet, sizeof(packet));
  delay(500);
  
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
  // Store command
  uint8_t packet[] = {0xEF, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x01, 0x00, 0x06, 0x06, 0x01, 0x00, id, 0x00, 0x00};
  
  // Calculate checksum
  uint16_t sum = 0x01 + 0x00 + 0x06 + 0x06 + 0x01 + 0x00 + id;
  packet[13] = (sum >> 8) & 0xFF;
  packet[14] = sum & 0xFF;
  
  while (mySerial.available()) mySerial.read();
  mySerial.write(packet, sizeof(packet));
  delay(500);
  
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

// File: esp32_code/fingerprint_enroll/fingerprint_enroll.ino