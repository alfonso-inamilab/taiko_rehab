// Basic demo for accelerometer readings from Adafruit MPU6050

#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>
#include <M5StickC.h>


Adafruit_MPU6050 mpu;

const float SENSOR_MASS = 0.100f;  // in kilograms (for force calculation)

void setup(void) {
  M5.begin();
  Wire.begin(0,26);    // SDA and SCL pin numbers
  M5.Lcd.setRotation(3);
  M5.Lcd.fillScreen(BLACK);
  M5.Lcd.setTextSize(1);
  
  Serial.begin(115200);
  while (!Serial)
    delay(10); // will pause Zero, Leonardo, etc until serial console opens

  Serial.println("MPU6050 though M5Stick started.");

  // Try to initialize!
  if (!mpu.begin()) {
    M5.Lcd.setTextColor(YELLOW);
    M5.Lcd.println("Fail - No acc detected ");
    M5.Lcd.println("MPU connections : ");
    M5.Lcd.println("M5Stick   Accelerometer");
    M5.Lcd.println("  5V          VCC");
    M5.Lcd.println("  GND         GND");
    M5.Lcd.println("  G26         SDA");
    M5.Lcd.println("  G0          SCL");

    while (1) {
      delay(10);
    }
  }
  M5.Lcd.println("MPU6050 Found!");

  mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
  M5.Lcd.println(" Acc. range 8G");
  delay(100);
  
  M5.Lcd.println("  X       Y       Z");
}

/* Variables to save accelertion and force */
float acc_x =0.0f; float acc_y =0.0f; float acc_z =0.0f;
float f_x =0.0f; float f_y =0.0f; float f_z =0.0f;
void loop() {
  /* Get new sensor events with the readings */
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);

  /* Get acceleration and calculate force */
  acc_x = a.acceleration.x;  acc_y = a.acceleration.y;  acc_z = a.acceleration.z;
  f_x = acc_x * SENSOR_MASS; f_y = acc_y * SENSOR_MASS; f_z = acc_z * SENSOR_MASS;

  /* Print out the values */
  M5.Lcd.setCursor(0, 25); 
  M5.Lcd.printf("%.2f   %.2f   %.2f ", acc_x , acc_y, acc_z);

  M5.Lcd.println("");
  M5.Lcd.println("Force");
  M5.Lcd.println("  X       Y       Z");
  
  M5.Lcd.printf("%.2f   %.2f   %.2f ", f_x , f_y, f_z);
  
  /* Send acc a though Serial to the PC    */
  Serial.printf( "%.4f ,  %.4f ,  %.4f  \n", acc_x , acc_y, acc_z);

  delay(10);
}
