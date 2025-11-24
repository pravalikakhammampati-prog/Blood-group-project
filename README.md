# Blood-group-project
## Connections 

```
R307 Sensor → ESP32 DOIT DevKit V1
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RED    → 5V (or 3.3V)
BLACK  → GND
YELLOW → GPIO 16 (RX2)
GREEN  → GPIO 17 (TX2)
BLUE   → Not connected
WHITE  → Not connected
```

RED    → 5V (or 3.3V)
BLACK  → GND
YELLOW → GPIO 16 (RX2)
GREEN  → GPIO 17 (TX2)
BLUE   → 
WHITE  → tx2



## Verification kosam

```
#include <Adafruit_Fingerprint.h>

// Use Hardware Serial 2 on ESP32
#define RX_PIN 16  // ESP32 RX2 to sensor TX (GREEN wire)
#define TX_PIN 17  // ESP32 TX2 to sensor RX (YELLOW wire)

HardwareSerial mySerial(2);  // Use UART2
Adafruit_Fingerprint finger = Adafruit_Fingerprint(&mySerial);

void setup() {
  Serial.begin(115200);  // USB Serial for monitoring
  delay(1000);
  
  Serial.println("\n\n=================================");
  Serial.println("R307 Fingerprint Sensor Test");
  Serial.println("ESP32 DOIT DevKit V1");
  Serial.println("=================================\n");
  
  // Initialize hardware serial for fingerprint sensor
  mySerial.begin(57600, SERIAL_8N1, RX_PIN, TX_PIN);
  delay(500);
  
  Serial.println("Testing sensor communication...");
  
  if (finger.verifyPassword()) {
    Serial.println("✓ Sensor found and working!");
    Serial.println("✓ Blue LED behavior is NORMAL (blinks on power, then off)");
  } else {
    Serial.println("✗ Sensor NOT found!");
    Serial.println("\n--- Troubleshooting Steps ---");
    Serial.println("1. Check RED wire → 5V or 3.3V");
    Serial.println("2. Check BLACK wire → GND");
    Serial.println("3. Check YELLOW wire → GPIO 16");
    Serial.println("4. Check GREEN wire → GPIO 17");
    Serial.println("5. Try swapping YELLOW ↔ GREEN if still fails");
    Serial.println("6. Measure voltage: RED to BLACK should be 3.3-5V");
    Serial.println("\nRunning baud rate scan...");
    scanBaudRates();
    while (1) { delay(1); }
  }
  
  // Get sensor parameters
  Serial.println("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
  Serial.println("    SENSOR INFORMATION");
  Serial.println("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
  Serial.print("Status Register: 0x"); Serial.println(finger.status_reg, HEX);
  Serial.print("System ID: 0x"); Serial.println(finger.system_id, HEX);
  Serial.print("Capacity: "); Serial.print(finger.capacity); Serial.println(" fingerprints");
  Serial.print("Security Level: "); Serial.println(finger.security_level);
  Serial.print("Device Address: 0x"); Serial.println(finger.device_addr, HEX);
  Serial.print("Packet Length: "); Serial.println(finger.packet_len);
  Serial.print("Baud Rate: "); Serial.println(finger.baud_rate);
  
  Serial.println("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
  Serial.println("    SENSOR STATUS");
  Serial.println("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
  Serial.println("✓ Communication: OK");
  Serial.println("✓ Power Supply: OK");
  Serial.println("✓ UART Connection: OK");
  Serial.println("✓ Sensor Ready!");
  
  Serial.println("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
  Serial.println("Place your finger on the sensor to test detection...");
  Serial.println("(Waiting for finger...)\n");
}

void loop() {
  uint8_t result = getFingerprintID();
  delay(500);
}

uint8_t getFingerprintID() {
  uint8_t p = finger.getImage();
  
  switch (p) {
    case FINGERPRINT_OK:
      Serial.println("\n━━━━━━━━━━━━━━━━━━━━━━━━━");
      Serial.println("✓✓✓ FINGERPRINT DETECTED! ✓✓✓");
      Serial.println("━━━━━━━━━━━━━━━━━━━━━━━━━");
      Serial.println("✓ Image captured successfully");
      Serial.println("✓ Sensor is WORKING PERFECTLY!\n");
      
      // Convert image to template
      p = finger.image2Tz();
      if (p == FINGERPRINT_OK) {
        Serial.println("✓ Image converted successfully");
        Serial.println("✓ Sensor fully functional!\n");
      }
      delay(2000);
      Serial.println("Remove finger and try again...\n");
      break;
      
    case FINGERPRINT_NOFINGER:
      Serial.print(".");  // Still waiting
      break;
      
    case FINGERPRINT_PACKETRECIEVEERR:
      Serial.println("\n✗ Communication error - check wiring!");
      break;
      
    case FINGERPRINT_IMAGEFAIL:
      Serial.println("\n✗ Imaging error - sensor may be dirty");
      break;
      
    default:
      Serial.print("\n✗ Unknown error: ");
      Serial.println(p);
      break;
  }
  
  return p;
}

void scanBaudRates() {
  long baudRates[] = {9600, 19200, 38400, 57600, 115200};
  
  Serial.println("\nScanning different baud rates...");
  for (int i = 0; i < 5; i++) {
    Serial.print("Trying: ");
    Serial.print(baudRates[i]);
    Serial.print(" baud... ");
    
    mySerial.end();
    delay(100);
    mySerial.begin(baudRates[i], SERIAL_8N1, RX_PIN, TX_PIN);
    delay(500);
    
    if (finger.verifyPassword()) {
      Serial.println("✓ SUCCESS!");
      Serial.print("Your sensor uses: ");
      Serial.print(baudRates[i]);
      Serial.println(" baud");
      return;
    } else {
      Serial.println("✗ No response");
    }
  }
  Serial.println("\n✗ No response at any baud rate - check power and wiring!");
}
```
