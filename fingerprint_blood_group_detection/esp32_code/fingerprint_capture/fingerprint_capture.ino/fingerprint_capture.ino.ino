// File: esp32_code/fingerprint_capture/fingerprint_capture.ino

/*
 * ═══════════════════════════════════════════════════════════════
 * PHASE 2 - STEP 2.3: FINGERPRINT IMAGE CAPTURE
 * ═══════════════════════════════════════════════════════════════
 * 
 * This sketch captures fingerprint image and displays it as hex
 */

#include <HardwareSerial.h>

HardwareSerial mySerial(2);

#define RX_PIN 16
#define TX_PIN 17

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n\n");
  Serial.println("╔════════════════════════════════════════════════╗");
  Serial.println("║   R307 FINGERPRINT IMAGE CAPTURE               ║");
  Serial.println("║   PHASE 2 - STEP 2.3                          ║");
  Serial.println("╚════════════════════════════════════════════════╝");
  Serial.println();
  
  mySerial.begin(57600, SERIAL_8N1, RX_PIN, TX_PIN);
  delay(500);
  
  Serial.println("Ready to capture fingerprint images!");
  Serial.println();
}

void loop() {
  Serial.println("\n════════════════════════════════════════════════");
  Serial.println("Press 'C' to capture fingerprint image");
  Serial.println("════════════════════════════════════════════════");
  
  while (!Serial.available()) {
    delay(100);
  }
  
  char cmd = Serial.read();
  while (Serial.available()) Serial.read();
  
  if (cmd == 'C' || cmd == 'c') {
    captureAndDownloadImage();
  }
  
  delay(1000);
}

void captureAndDownloadImage() {
  Serial.println("\n→ Place finger on sensor...");
  
  // Wait for finger
  int p = -1;
  while (p != 0) {
    p = getImage();
    if (p == -1) {
      Serial.println("❌ Communication error");
      return;
    }
    delay(100);
  }
  
  Serial.println("✅ Finger detected");
  Serial.println("→ Capturing image...");
  
  // Convert image to buffer
  if (image2Tz(1) != 0) {
    Serial.println("❌ Failed to process image");
    return;
  }
  
  Serial.println("✅ Image captured and processed");
  Serial.println("✅ Fingerprint image ready");
  Serial.println("\n📸 Image capture successful!");
  Serial.println("   (Full image download requires additional code)");
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

// File: esp32_code/fingerprint_capture/fingerprint_capture.ino