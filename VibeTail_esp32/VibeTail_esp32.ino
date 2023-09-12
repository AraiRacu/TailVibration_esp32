#include <ArduinoOSCWiFi.h>
#include <math.h>
 
const char* ssid = "SSID"; //WiFIのSSIDを入力
const char* pass = "Pass"; // WiFiのパスワードを入力

const IPAddress ip(192, 168, XX, XX); //自身のIPアドレス
const IPAddress gateway(192, 168, XX, XX);  //デフォルトゲートウェイ
const IPAddress subnet(255, 255, XX, XX); //サブネットマスク

const char *pc_addr = "192.168.XX.XX";  //送信元のPCのIPアドレス
const int pc_port = XXXX; //受信先のポート

// モータ制御
const int PWMA = 2;
const int AIN1 = 18;
const int AIN2 = 19;
const int PWMB = 4;
const int BIN1 = 16;
const int BIN2 = 17;
const int STBY = 5;
const int LEDCA_CHANNEL = 0;
const int LEDCB_CHANNEL = 1;
const int LEDC_BASE_FREQ = 8000;

void setup() {
  Serial.begin(115200);
  SetPin();
  SetWifi();
 
  GetWiFiConfig();

  OscWiFi.subscribe(pc_port, "/motor1", onOscReceived);
  OscWiFi.subscribe(pc_port, "/motor2", onOscReceived2);
}

void SetWifi(){
  //Wifi Setup
  #ifdef ESP_PLATFORM
    WiFi.disconnect(true, true);  // disable wifi, erase ap info
    delay(1000);
    WiFi.mode(WIFI_STA);
  #endif
  WiFi.begin(ssid, pass);
  WiFi.config(ip, gateway, subnet);
 
  Serial.println("WiFi Connected");
}

void SetPin(){
  // PWMの初期化
  ledcSetup(LEDCA_CHANNEL, LEDC_BASE_FREQ, 8);
  ledcAttachPin(PWMA, LEDCA_CHANNEL);
  ledcSetup(LEDCB_CHANNEL, LEDC_BASE_FREQ, 8);
  ledcAttachPin(PWMB, LEDCB_CHANNEL);

  // GPIOピンの初期化
  pinMode(AIN1, OUTPUT);
  pinMode(AIN2, OUTPUT);
  pinMode(BIN1, OUTPUT);
  pinMode(BIN2, OUTPUT);
  pinMode(STBY, OUTPUT);

  digitalWrite(STBY, HIGH);
}
 
void GetWiFiConfig() {
  Serial.print("IP address:");
  Serial.println(WiFi.localIP());
  Serial.print("default gateway:");
  Serial.println(WiFi.gatewayIP());
  Serial.print("subnetmask:");
  Serial.println(WiFi.subnetMask());
  Serial.print("DNS Server1:");
  Serial.println(WiFi.dnsIP(0));
  Serial.print("DNS Server2:");
  Serial.println(WiFi.dnsIP(1));
 
  byte mac_addr[6];
  WiFi.macAddress(mac_addr);
  Serial.print("mac address:");
  for(int i = 0; i < 6; i++){
    Serial.print(mac_addr[i], HEX);
 
    if(i < 5){
      Serial.print(":");
    }else{
      Serial.println("");
    }
  }
}
 
void loop() {
  OscWiFi.parse();
  delay(10);  // Delay 10ms.
}

void onOscReceived(const OscMessage& m){
  float received_parm = m.arg<float>(0);
  mortorController(AIN1, AIN2, LEDCA_CHANNEL, received_parm);
}

void onOscReceived2(const OscMessage& m){
  float received_parm = m.arg<float>(0);
  mortorController(BIN1, BIN2, LEDCB_CHANNEL, received_parm);
}

void mortorController(const int IN1, const int IN2, const int CHANNEL, const float value){
  Serial.println("Receive any");
  Serial.println(value);
  if(value == 0){
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, LOW); 
  }else{
    digitalWrite(IN1, HIGH);
    digitalWrite(IN2, LOW);
    double x = double(value);
    //y=30(1.8Logx +2)
    double y = (1.8 * log10(x) + 2) * 30;
    //y=12 * 5 ^ x
    //double y = 12 * pow(5, x);

    ledcWrite(CHANNEL, int(y));
    Serial.println(y);
  }
}