#include <Adafruit_Fingerprint.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// LCD setup
LiquidCrystal_I2C lcd(0x27, 16, 2);

// Fingerprint sensor pins
HardwareSerial FingerprintSerial(2);  // RX2, TX2 for ESP32

Adafruit_Fingerprint finger = Adafruit_Fingerprint(&FingerprintSerial);

// Sample blood group mapping (You can change this)
String getBloodGroup(uint8_t id) {
  switch (id) {
    case 1: return "A+";
    case 2: return "A-";
    case 3: return "B+";
    case 4: return "B-";
    case 5: return "O+";
    case 6: return "O-";
    case 7: return "AB+";
    case 8: return "AB-";
    default: return "Unknown";
  }
}

void setup() {
  Serial.begin(115200);

  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("Blood Group");
  lcd.setCursor(0, 1);
  lcd.print("Detection");

  delay(2000);
  lcd.clear();

  // Fingerprint Sensor Start
  FingerprintSerial.begin(57600, SERIAL_8N1, 16, 17); // RX=16, TX=17

  finger.begin(57600);

  if (finger.verifyPassword()) {
    lcd.print("Sensor Ready");
  } else {
    lcd.print("Sensor Error!");
    while (1);
  }

  delay(1500);
  lcd.clear();
}

void loop() {
  lcd.setCursor(0, 0);
  lcd.print("Place Finger");

  int result = finger.getImage();

  if (result == FINGERPRINT_OK) {
    lcd.clear();
    lcd.print("Reading...");
    delay(500);

    finger.image2Tz();
    finger.fingerSearch();

    if (finger.fingerID > 0) {
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Finger ID: ");
      lcd.print(finger.fingerID);

      lcd.setCursor(0, 1);
      lcd.print("Group: ");
      lcd.print(getBloodGroup(finger.fingerID));
      delay(3000);
    } else {
      lcd.clear();
      lcd.print("Not Found");
      delay(1500);
    }
  }

  delay(500);
}

