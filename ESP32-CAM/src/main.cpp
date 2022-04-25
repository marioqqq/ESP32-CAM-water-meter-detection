#include <Arduino.h>

// Enable Debug interface and serial prints over UART1
#define DEGUB_ESP

// WiFi libraries
#include <WiFi.h>
#include "esp_wifi.h"

// MQTT
extern "C"
{
#include "freertos/FreeRTOS.h"
#include "freertos/timers.h"
}

#include <AsyncMqttClient.h>

// Camera related
#include "esp_camera.h"
#include "esp_timer.h"
#include "img_converters.h"

#include "fb_gfx.h"
#include "fd_forward.h"
#include "fr_forward.h"
//#include "dl_lib.h"

#include "driver/adc.h"
#include <esp_bt.h>

// Connection timeout;
#define CON_TIMEOUT 10 * 1000 // milliseconds

// Not using Deep Sleep on PCB because TPL5110 timer takes over.
#define TIME_TO_SLEEP (uint64_t)30 * 60 * 1000 * 1000 // 10*60*1000*1000   // microseconds

// WiFi Credentials
#define WIFI_SSID "WIFI"
#define WIFI_PASSWORD "PASS"

// Set your Static IP address
IPAddress local_IP(192, 168, 100, 30);
// Set your Gateway IP address
IPAddress gateway(192, 168, 100, 1);
IPAddress subnet(255, 255, 0, 0);

// MQTT Broker configuration
#define MQTT_HOST "MQTT_HOST"
#define MQTT_PORT 1883
#define USERNAME "MQTT_broaker"
#define PASSWORD "pass"
#define TOPIC_PIC "test"

#define LED 4

#ifdef DEGUB_ESP
#define DBG(x) Serial.println(x)
#else
#define DBG(...)
#endif

// Camera buffer, URL and picture name
camera_fb_t *fb = NULL;

// MQTT callback
AsyncMqttClient mqttClient;
TimerHandle_t mqttReconnectTimer;
TimerHandle_t wifiReconnectTimer;

bool camera_init()
{
  // IF USING A DIFFERENT BOARD, NEED DIFFERENT PINs
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = 5;
  config.pin_d1 = 18;
  config.pin_d2 = 19;
  config.pin_d3 = 21;
  config.pin_d4 = 36;
  config.pin_d5 = 39;
  config.pin_d6 = 34;
  config.pin_d7 = 35;
  config.pin_xclk = 0;
  config.pin_pclk = 22;
  config.pin_vsync = 25;
  config.pin_href = 23;
  config.pin_sscb_sda = 26;
  config.pin_sscb_scl = 27;
  config.pin_pwdn = 32;
  config.pin_reset = -1;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;

  // init with high specs to pre-allocate larger buffers
  config.frame_size = FRAMESIZE_UXGA; // set picture size, FRAMESIZE_QQVGA = 1600x1200
  config.jpeg_quality = 30;           // quality of JPEG output. 0-63 lower means higher quality
  config.fb_count = 2;

  // camera init
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK)
  {
    Serial.print("Camera init failed with error 0x%x");
    DBG(err);
    return false;
  }
  else
  {
    return true;
  }
}

void deep_sleep()
{
  DBG("Going to sleep after: " + String(millis()) + "ms");
  Serial.flush();
  WiFi.disconnect(true);
  WiFi.mode(WIFI_OFF);
  btStop();

  esp_wifi_stop();
  esp_bt_controller_disable();
  // SD card
  pinMode(14, INPUT);
  pinMode(12, INPUT_PULLUP);
  pinMode(13, INPUT_PULLUP);
  pinMode(15, INPUT_PULLUP);
  pinMode(2, INPUT_PULLUP);
  pinMode(4, INPUT);
  // Camera
  pinMode(36, INPUT);
  pinMode(39, INPUT);
  pinMode(34, INPUT);
  pinMode(35, INPUT);
  pinMode(25, INPUT);
  pinMode(0, INPUT);
  pinMode(5, INPUT);
  pinMode(18, INPUT);
  pinMode(19, INPUT);
  pinMode(21, INPUT);
  pinMode(22, INPUT_PULLDOWN);
  pinMode(23, INPUT);
  pinMode(32, INPUT);
  pinMode(26, INPUT_PULLUP);
  pinMode(27, INPUT_PULLUP);

  pinMode(33, INPUT_PULLUP);

  esp_deep_sleep_start();
}

void connectWiFi()
{

  DBG("Connecting to Wi-Fi...");
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  while (WiFi.status() != WL_CONNECTED && millis() < CON_TIMEOUT)
  {
    delay(500);
    Serial.print(".");
  }

  if (WiFi.status() != WL_CONNECTED)
  {
    DBG("Failed to connect to WiFi");
    delay(500);
    deep_sleep();
  }

  DBG();
  DBG("IP address: ");
  DBG(WiFi.localIP());
}

void connectMQTT()
{
  DBG("Connecting to MQTT...");
  mqttClient.connect();

  while (!mqttClient.connected() && millis() < CON_TIMEOUT)
  {
    delay(500);
    Serial.print(".");
  }

  if (!mqttClient.connected())
  {
    DBG("Failed to connect to MQTT Broker");
    deep_sleep();
  }
}

bool take_picture()
{
  DBG("Taking picture now");
  fb = esp_camera_fb_get();

  if (!fb)
  {
    DBG("Camera capture failed");
    return false;
  }

  DBG("Camera capture success");

  return true;
}

void onMqttConnect(bool sessionPresent)
{
  // Take picture
  digitalWrite(LED, HIGH);
  delay(100);
  take_picture();
  digitalWrite(LED, LOW);

  // Publish picture
  const char *pic_buf = (const char *)(fb->buf);
  size_t length = fb->len;
  mqttClient.publish(TOPIC_PIC, 1, false, pic_buf, length);
}

void onMqttPublish(uint16_t packetId)
{
  Serial.println("Publish acknowledged.");
  Serial.print("  packetId: ");
  Serial.println(packetId);
  deep_sleep();
}

void setup()
{
#ifdef DEGUB_ESP
  Serial.begin(115200);
  Serial.setDebugOutput(true);
#endif

  pinMode(LED, OUTPUT);

  setCpuFrequencyMhz(80);

  /*if (!WiFi.config(local_IP, gateway, subnet))
  {
    DBG("STA Failed to configure");
  }*/

  // Configure MQTT Broker and callback
  mqttReconnectTimer = xTimerCreate("mqttTimer", pdMS_TO_TICKS(2000), pdFALSE, (void *)0, reinterpret_cast<TimerCallbackFunction_t>(connectMQTT));
  mqttClient.setCredentials(USERNAME, PASSWORD);
  mqttClient.onConnect(onMqttConnect);
  mqttClient.onPublish(onMqttPublish);
  mqttClient.setServer(MQTT_HOST, MQTT_PORT);

  // Initialize and configure camera
  camera_init();

  // Enable timer wakeup for ESP32 sleep
  esp_sleep_enable_timer_wakeup(TIME_TO_SLEEP);

  connectWiFi();
  connectMQTT();
}

void loop() {}