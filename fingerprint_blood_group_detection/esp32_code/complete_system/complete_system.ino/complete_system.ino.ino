// File: esp32_code/complete_system/complete_system.ino

/*
 * ═══════════════════════════════════════════════════════════════
 * COMPLETE FINGERPRINT BLOOD GROUP DETECTION SYSTEM
 * PHASE 2 - STEP 2.4: INTEGRATED SYSTEM
 * ═══════════════════════════════════════════════════════════════
 * 
 * This system:
 * 1. Captures fingerprint
 * 2. Sends data to Python via Serial
 * 3. Receives blood group prediction
 * 4. Displays result
 */

#include <HardwareSerial.h>

HardwareSerial mySerial(2);

#define RX_PIN 16
#define TX_PIN 17

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n\n");
  Serial.println("╔═══════════════════════════════════════════════════════╗");
  Serial.println("║  FINGERPRINT BLOOD GROUP DETECTION SYSTEM             ║");
  Serial.println("║  COMPLETE INTEGRATED SYSTEM                           ║");
  Serial.println("╚═══════════════════════════════════════════════════════╝");
  Serial.println();
  
  mySerial.begin(57600, SERIAL_8N1, RX_PIN, TX_PIN);
  delay(500);
  
  Serial.println("System initialized!");
  Serial.println("Python inference server should be running.");
  Serial.println();
}

void loop() {
  Serial.println("\n═══════════════════════════════════════════════════════");
  Serial.println("BLOOD GROUP DETECTION MENU:");
  Serial.println("═══════════════════════════════════════════════════════");
  Serial.println("1. Press 'D' - Detect blood group from fingerprint");
  Serial.println("2. Press 'T' - Test sensor connection");
  Serial.println("═══════════════════════════════════════════════════════");
  
  while (!Serial.available()) {
    delay(100);
  }
  
  char cmd = Serial.read();
  while (Serial.available()) Serial.read();
  
  if (cmd == 'D' || cmd == 'd') {
    detectBloodGroup();
  } else if (cmd == 'T' || cmd == 't') {
    testSensor();
  }
  
  delay(2000);
}

void detectBloodGroup() {
  Serial.println("\n╔═══════════════════════════════════════════════════════╗");
  Serial.println("║           BLOOD GROUP DETECTION PROCESS               ║");
  Serial.println("╚═══════════════════════════════════════════════════════╝");
  
  // Step 1: Capture fingerprint
  Serial.println("\n[STEP 1/3] Capturing Fingerprint");
  Serial.println("→ Place finger on sensor...");
  
  int p = -1;
  int attempts = 0;
  while (p != 0 && attempts < 50) {
    p = getImage();
    if (p == -1) {
      Serial.println("❌ Sensor communication error");
      return;
    }
    attempts++;
    delay(100);
  }
  
  if (p != 0) {
    Serial.println("❌ Timeout: No finger detected");
    return;
  }
  
  Serial.println("✅ Finger detected");
  
  // Step 2: Process image
  Serial.println("\n[STEP 2/3] Processing Fingerprint Image");
  if (image2Tz(1) != 0) {
    Serial.println("❌ Failed to process fingerprint");
    return;
  }
  Serial.println("✅ Fingerprint processed");
  
  // Step 3: Send to Python for prediction
  Serial.println("\n[STEP 3/3] Sending to ML Model for Prediction");
  Serial.println("→ Sending fingerprint data to Python...");
  
  // Send marker for Python to detect
  Serial.println("FINGERPRINT_START");
  
  // In a real implementation, you would download the actual image here
  // For this demo, we'll send a placeholder
  Serial.println("FINGERPRINT_DATA:DEMO_MODE");
  
  Serial.println("FINGERPRINT_END");
  
  // Wait for response from Python
  Serial.println("→ Waiting for prediction...");
  
  unsigned long startTime = millis();
  String response = "";
  
  while (millis() - startTime < 5000) { // 5 second timeout
    if (Serial.available()) {
      char c = Serial.read();
      if (c == '\n') {
        if (response.startsWith("BLOOD_GROUP:")) {
          String bloodGroup = response.substring(12);
          bloodGroup.trim();
          
          Serial.println("\n╔═══════════════════════════════════════════════════════╗");
          Serial.println("║              PREDICTION RESULT                        ║");
          Serial.println("╚═══════════════════════════════════════════════════════╝");
          Serial.print("\n🩸 DETECTED BLOOD GROUP: ");
          Serial.println(bloodGroup);
          Serial.println("\n✅ Detection complete!");
          Serial.println("═══════════════════════════════════════════════════════");
          return;
        }
        response = "";
      } else {
        response += c;
      }
    }
    delay(10);
  }
  
  Serial.println("⚠️  No response from Python server");
  Serial.println("   Make sure inference server is running!");
}

void testSensor() {
  Serial.println("\n→ Testing R307 sensor...");
  
  uint8_t vfyPwd[] = {0xEF, 0x01, 0xFF, 0xFF, 0xFF, 0xFF, 0x01, 0x00, 0x07, 0x13, 0x00, 0x00, 0x00, 0x00, 0x00, 0x1B};
  
  while (mySerial.available()) mySerial.read();
  mySerial.write(vfyPwd, sizeof(vfyPwd));
  delay(200);
  
  if (mySerial.available() >= 12) {
    uint8_t response[12];
    for (int i = 0; i < 12; i++) {
      response[i] = mySerial.read();
    }
    
    if (response[0] == 0xEF && response[1] == 0x01 && response[9] == 0x00) {
      Serial.println("✅ R307 sensor is working correctly");
      return;
    }
  }
  
  Serial.println("❌ Sensor not responding");
}

int getImage() {
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

// File: esp32_code/complete_system/complete_system.ino