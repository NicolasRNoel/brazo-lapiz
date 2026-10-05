/* ==========================================================================
   TECLADO MATRICIAL 4x4 + LCD I2C -> ESP32 -> PC (PyBullet)
   ==========================================================================
   Envia la tecla pulsada a la PC por serial a 115200 baud.

   CORREGIDO respecto a la version que no arrancaba:
     - GPIO 12 es un "strapping pin" (MTDI) del ESP32. La libreria Keypad lo
       configura como INPUT_PULLUP, o sea que queda en ALTO durante el reset,
       y en varias placas eso impide que bootee. Aqui se usan pines seguros.
     - rowPins y colPins se separan en pines que no chocan con el I2C
       (GPIO 21 = SDA, 22 = SCL), ni con la flash (6-11), ni con PSRAM
       (16/17 en WROVER), ni con el USB nativo (19/20).
     - keypad.begin() explicito.

   CONEXIONES
     membrane 4x4      ESP32
     ------------      -----
     fila 1  (R1)      GPIO 13
     fila 2  (R2)      GPIO 14
     fila 3  (R3)      GPIO 18
     fila 4  (R4)      GPIO 23
     col 1   (C1)      GPIO 25
     col 2   (C2)      GPIO 26
     col 3   (C3)      GPIO 27
     col 4   (C4)      GPIO 32

     LCD 16x2 I2C      ESP32
     ------------      -----
     SDA                GPIO 21
     SCL                GPIO 22
     VCC                5V  (o 3V3, segun tu modulo)
     GND                GND

   En la PC: pip install pyserial
   ========================================================================== */

#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <Keypad.h>

// Direccion I2C tipica del modulo. Si no funciona, prueba 0x3F.
const int LCD_ADDR = 0x27;
LiquidCrystal_I2C lcd(LCD_ADDR, 16, 2);

const byte FILAS = 4;
const byte COLS  = 4;

// MATRIZ DE LA MEMBRANA. Si tu teclado esta cableado al reves, cambia el
// orden de las filas y/o columnas aqui.
char teclas[FILAS][COLS] = {
  {'1','2','3','A'},
  {'4','5','6','B'},
  {'7','8','9','C'},
  {'*','0','#','D'}
};

// Pines SEGUROS: nada de strapping (0,2,5,12,15), nada de flash (6-11),
// nada de PSRAM (16/17), nada de I2C (21/22), nada de USB nativo (19/20).
byte pinesFila[FILAS] = {13, 14, 18, 23};
byte pinesCol[COLS]   = {25, 26, 27, 32};

Keypad teclado = Keypad(makeKeymap(teclas), pinesFila, pinesCol, FILAS, COLS);

bool lcdOk = false;
unsigned long ultimoEnvio = 0;

void setup() {
  Serial.begin(115200);
  delay(200);                 // que el USB se estabilice antes de enviar nada

  Wire.begin(21, 22);
  lcd.init();
  lcd.backlight();
  lcdOk = true;
  lcd.setCursor(0, 0);
  lcd.print("Brazo: lista");
  lcd.setCursor(0, 1);
  lcd.print("Teclado 0-9 OK");

  teclado.begin();

  // Envia un '#' de arranque para que la PC sepa que la ESP32 arranco.
  // La PC lo ignora, pero sirve para sincronizar.
  Serial.println('#');
}

void loop() {
  char t = teclado.getKey();   // ya trae el debounce de la libreria

  if (t != NO_KEY) {
    // Refresca el LCD
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
