#include <WiFi.h>
#include <WiFiUDP.h>
#include <M5StickC.h>

// Get all IP addresses with arp -a 
// Get your own IP address with ipconfig

const  char ssid [] = "inamilab2.4G" ; // enter the WiFI SSID 
const  char pass [] = "Inami2016" ; // enter the WiFi password

WiFiUDP wifiUdp; 
const  char * pc_addr = "192.168.100.4" ; // "192.168.0.6" ;
const  int pc_port = 50007 ; // destination port 
const  int my_port = 50008 ;  // own port

// Variables to save the accel output
float accX = 0;
float accY = 0;
float accZ = 0;  
String msg = "";
int cycles = 0;

void setup() {
  M5.begin();
  
  //Configure screen  & init MPU
  M5.Lcd.setRotation(3);
  M5.Lcd.fillScreen(BLACK);
  M5.Lcd.setTextSize(1);
  M5.MPU6886.Init();

  // Init wifi
  WiFi.begin(ssid, pass);
  while( WiFi.status() != WL_CONNECTED) {
    delay(500); 
    //M5.Lcd.print("."); 
  }

  // LCD Output
  M5.Lcd.setCursor(0, 15);
  M5.Lcd.println("WiFi connected");
  M5.Lcd.print("IP address = ");
  M5.Lcd.println(WiFi.localIP());
  M5.Lcd.println("  X       Y       Z");

  wifiUdp.begin(my_port);   // Init UDP comms
}

void loop () {
  M5.MPU6886.getAccelData(&accX,&accY,&accZ);

  msg = "x" + String(accX*1000,3) + "xy" + String(accY*1000,3) + "yz" + String(accZ*1000,3) + "z" ;
  std::vector<uint8_t> myVector(msg.begin(), msg.end());
  uint8_t *p = &myVector[0];  
    
  // Data transmission
  wifiUdp.beginPacket(pc_addr, pc_port);
  wifiUdp.write(p, msg.length());
  wifiUdp.endPacket();

  M5.Lcd.setCursor(0, 45);
  if (cycles > 10 ){
    M5.Lcd.printf("%.2f   %.2f   %.2f      ",accX * 1000, accY * 1000, accZ * 1000);
    cycles = 0;
  } 
  cycles = cycles + 1;
  delay(5);
}
