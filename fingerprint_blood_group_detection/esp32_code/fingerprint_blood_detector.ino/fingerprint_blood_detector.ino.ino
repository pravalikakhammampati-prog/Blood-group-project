// File: fingerprint_blood_detector.ino

/*
 * ═══════════════════════════════════════════════════════════════
 * FINGERPRINT BLOOD GROUP DETECTION - WORKING VERSION
 * Uses Adafruit_Fingerprint library for reliability
 * ═══════════════════════════════════════════════════════════════
 */

#include <Adafruit_Fingerprint.h>

// Hardware Serial for R307
#define RX_PIN 16  // ESP32 RX2 → Sensor TX (GREEN wire)
#define TX_PIN 17  // ESP32 TX2 → Sensor RX (YELLOW wire)

HardwareSerial mySerial(2);
Adafruit_Fingerprint finger = Adafruit_Fingerprint(&mySerial);

uint8_t nextID = 1;
bool systemReady = false;

void setup() {
  Serial.begin(115200);
  delay(2000);
  
  Serial.println("\n\n╔═══════════════════════════════════════════════════════╗");
  Serial.println("║  FINGERPRINT BLOOD GROUP DETECTION - QUICK DEMO      ║");
  Serial.println("║  >>> PLACE FINGER TO GET BLOOD GROUP <<<             ║");
  Serial.println("╚═══════════════════════════════════════════════════════╝\n");
  
  // Initialize sensor
  mySerial.begin(57600, SERIAL_8N1, RX_PIN, TX_PIN);
  delay(500);
  
  Serial.println("→ Initializing R307 sensor...");
  
  if (finger.verifyPassword()) {
    Serial.println("✅ R307 sensor connected!");
    systemReady = true;
  } else {
    Serial.println("❌ Sensor NOT found!");
    Serial.println("\n⚠️  TROUBLESHOOTING:");
    Serial.println("   1. Check RED wire → 5V");
    Serial.println("   2. Check BLACK wire → GND");
    Serial.println("   3. Check YELLOW wire → GPIO 16");
    Serial.println("   4. Check GREEN wire → GPIO 17");
    Serial.println("   5. Try 3.3V instead of 5V if using 5V");
    
    while (1) {
      delay(1000);
    }
  }
  
  // Get sensor info
  Serial.println("→ Reading sensor parameters...");
  finger.getParameters();
  
  Serial.println("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
  Serial.print("   Sensor ID: 0x"); Serial.println(finger.system_id, HEX);
  Serial.print("   Capacity: "); Serial.print(finger.capacity); Serial.println(" fingerprints");
  Serial.print("   Security Level: "); Serial.println(finger.security_level);
  Serial.println("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n");
  
  Serial.println("✅ System ready!");
  Serial.println("✅ Python server should be running\n");
  Serial.println("═══════════════════════════════════════════════════════");
  Serial.println(">>> PLACE YOUR FINGER ON THE SENSOR <<<");
  Serial.println("═══════════════════════════════════════════════════════\n");
}

void loop() {
  if (!systemReady) {
    delay(1000);
    return;
  }
  
  // Check for finger
  uint8_t result = finger.getImage();
  
  if (result == FINGERPRINT_OK) {
    // Finger detected!
    Serial.println("\n🖐️  FINGER DETECTED!");
    Serial.println("→ Processing fingerprint...");
    
    // Convert image
    result = finger.image2Tz(1);
    if (result != FINGERPRINT_OK) {
      Serial.println("❌ Failed to process fingerprint");
      delay(2000);
      return;
    }
    
    Serial.println("✅ Fingerprint captured");
    
    // Search for match
    result = finger.fingerSearch();
    
    if (result == FINGERPRINT_OK) {
      Serial.print("✅ Recognized! ID #");
      Serial.print(finger.fingerID);
      Serial.print(" (Confidence: ");
      Serial.print(finger.confidence);
      Serial.println(")");
    } else {
      Serial.println("→ New fingerprint - Auto-enrolling...");
      
      if (enrollNewFinger()) {
        Serial.print("✅ Enrolled as ID #");
        Serial.println(nextID - 1);
      } else {
        Serial.println("⚠️  Quick enrollment skipped");
      }
    }
    
    // Now get blood group prediction
    Serial.println("\n🔮 DETECTING BLOOD GROUP...");
    Serial.println("PREDICT_NOW");
    
    // Wait for Python response
    unsigned long startTime = millis();
    String response = "";
    bool gotResult = false;
    
    while (millis() - startTime < 5000) {
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
            Serial.println("═══════════════════════════════════════════════════╝");
            Serial.println();
            
            gotResult = true;
            break;
          }
          response = "";
        } else {
          response += c;
        }
      }
      delay(10);
    }
    
    if (!gotResult) {
      Serial.println("⚠️  No response from Python (is server running?)");
    }
    
    Serial.println("\n═══════════════════════════════════════════════════════");
    Serial.println(">>> REMOVE FINGER, THEN PLACE AGAIN FOR NEXT TEST <<<");
    Serial.println("═══════════════════════════════════════════════════════\n");
    
    // Wait for finger removal
    delay(2000);
    while (finger.getImage() == FINGERPRINT_OK) {
      delay(100);
    }
    delay(1000);
    
    Serial.println("Ready for next fingerprint...\n");
  }
  
  delay(50);
}

bool enrollNewFinger() {
  // Ask to remove finger
  Serial.println("   → Remove finger...");
  delay(2000);
  
  // Wait for finger removal
  while (finger.getImage() == FINGERPRINT_OK) {
    delay(50);
  }
  
  Serial.println("   → Place SAME finger again...");
  
  // Wait for same finger (timeout after 10 seconds)
  int attempts = 0;
  while (attempts < 200) {
    if (finger.getImage() == FINGERPRINT_OK) {
      break;
    }
    delay(50);
    attempts++;
  }
  
  if (attempts >= 200) {
    Serial.println("   ⚠️  Timeout - enrollment canceled");
    return false;
  }
  
  // Convert second image
  uint8_t p = finger.image2Tz(2);
  if (p != FINGERPRINT_OK) {
    Serial.println("   ❌ Failed to process second image");
    return false;
  }
  
  // Create model
  p = finger.createModel();
  if (p != FINGERPRINT_OK) {
    Serial.println("   ❌ Fingers didn't match");
    return false;
  }
  
  // Store model
  p = finger.storeModel(nextID);
  if (p != FINGERPRINT_OK) {
    Serial.println("   ❌ Failed to store model");
    return false;
  }
  
  nextID++;
  return true;
}

// File: fingerprint_blood_detector.ino