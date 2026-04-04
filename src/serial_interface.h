#pragma once

#include <Arduino.h>

// Forward declaration of processCommand from main.cpp
void processCommand(char* command);

namespace SerialInterface {

void setup();
void update();
bool isConnected();

}  // namespace SerialInterface
