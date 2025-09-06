// 7-Segment pins (a-g) -> D7-D13
int segPins[] = {7, 8, 9, 10, 11, 12, 13};

// LED pins -> D2-D6
int leds[] = {2, 3, 4, 5, 6};

// 7-Segment pattern (common cathode)
int numbers[10][7] = {
  {1,1,1,1,1,1,0}, // 0
  {0,1,1,0,0,0,0}, // 1
  {1,1,0,1,1,0,1}, // 2
  {1,1,1,1,0,0,1}, // 3
  {0,1,1,0,0,1,1}, // 4
  {1,0,1,1,0,1,1}, // 5
  {1,0,1,1,1,1,1}, // 6
  {1,1,1,0,0,0,0}, // 7
  {1,1,1,1,1,1,1}, // 8
  {1,1,1,1,0,1,1}  // 9
};

void setup() {
  Serial.begin(9600);

  for (int i=0; i<7; i++) pinMode(segPins[i], OUTPUT);
  for (int i=0; i<5; i++) pinMode(leds[i], OUTPUT);
}

void showNumber(int num) {
  if (num < 0 || num > 9) return;
  for (int i=0; i<7; i++) {
    digitalWrite(segPins[i], numbers[num][i]);
  }
}

void loop() {
  if (Serial.available()) {
    int fingerCount = Serial.readStringUntil('\n').toInt();

    // แสดงเลขบน 7-Segment
    showNumber(fingerCount);

    // เปิด LED ตามจำนวน
    for (int i = 0; i < 5; i++) {
      if (i < fingerCount) digitalWrite(leds[i], HIGH);
      else digitalWrite(leds[i], LOW);
    }
  }
}
