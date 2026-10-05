/* ==========================================================================
   TECLADO MATRICIAL 4x4 + LCD I2C -> ESP32 -> PC (PyBullet)
   ==========================================================================
  

#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <Keypad.h>


const int LCD_ADDR = 0x27;
LiquidCrystal_I2C lcd(LCD_ADDR, 16, 2);

const byte FILAS = 4;
const byte COLS  = 4;

char teclas[FILAS][COLS] = {
  {'1','2','3','A'},
  {'4','5','6','B'},
  {'7','8','9','C'},
  {'*','0','#','D'}
};

byte pinesFila[FILAS] = {13, 14, 18, 23};
byte pinesCol[COLS]   = {25, 26, 27, 32};

Keypad teclado = Keypad(makeKeymap(teclas), pinesFila, pinesCol, FILAS, COLS);

bool lcdOk = false;
unsigned long ultimoEnvio = 0;

void setup() {
  Serial.begin(115200);
  delay(200);            

  Wire.begin(21, 22);
  lcd.init();
  lcd.backlight();
  lcdOk = true;
  lcd.setCursor(0, 0);
  lcd.print("Brazo: lista");
  lcd.setCursor(0, 1);
  lcd.print("Teclado 0-9 OK");

  teclado.begin();

  Serial.println('#');
}

void loop() {
  char t = teclado.getKey();   

  if (t != NO_KEY) {
 
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Tecla:");
    lcd.setCursor(6, 0);
    lcd.print(t);
    lcd.setCursor(0, 1);
    if (t >= '0' && t <= '9') {
      lcd.print("Mandando...");
    } else {
      lcd.print("Sin digito");  // A B C # *
    }

    Serial.println(t);          // manda '1', '2', ... y un \n
    ultimoEnvio = millis();
  }
}
