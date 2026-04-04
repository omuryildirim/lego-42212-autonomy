#pragma once

#include <Arduino.h>

// Forward declaration of processCommand from main.cpp
void processCommand(char* command);

namespace BLEInterface {

void setup();
void update();
bool isConnected();

}  // namespace BLEInterface
