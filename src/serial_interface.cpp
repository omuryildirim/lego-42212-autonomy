#include "serial_interface.h"
#include <string.h>

// Forward declaration - implemented in main.cpp
void processCommand(char* line);
void printHelp();

namespace SerialInterface {

char commandBuffer[96];
size_t commandLength = 0;
bool connected = false;

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("Serial interface ready");
  printHelp();
  connected = true;
}

void readSerialCommands() {
  while (Serial.available() > 0) {
    const char incoming = static_cast<char>(Serial.read());

    if (incoming == '\r') {
      continue;
    }

    if (incoming == '\n') {
      commandBuffer[commandLength] = '\0';
      if (commandLength > 0) {
        processCommand(commandBuffer);
      }
      commandLength = 0;
      continue;
    }

    if (commandLength + 1 < sizeof(commandBuffer)) {
      commandBuffer[commandLength++] = incoming;
    }
  }
}

void update() {
  readSerialCommands();
}

bool isConnected() {
  return connected;
}

}  // namespace SerialInterface
