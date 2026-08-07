#include <Arduino.h>
#include <math.h>

// 1. Define PIN
#define PIN_X_STEP 4
#define PIN_X_DIR 5

#define PIN_Y_STEP 6
#define PIN_Y_DIR 7

#define PIN_Z_STEP 15
#define PIN_Z_DIR 16

#define PIN_ENABLE 17

// 2. Lead screw (STEP per mm)
const float STEP_PER_MM_X = 400.0f;
const float STEP_PER_MM_Y = 400.0f;
const float STEP_PER_MM_Z = 400.0f;

// 3. Default Feedrate (mm/min)
const float DEFAULT_FR = 300.0f; 

// 4. Structure of Target Point
struct targetPoint {
    int now_g;
    long x_step;
    long y_step;
    long z_step;
    uint32_t delay_step_microsec;
};

// 5. Establish Queue
QueueHandle_t targetQ;

// 6. Status Available from CPU to RAM
volatile long current_step_x = 0;
volatile long current_step_y = 0;
volatile long current_step_z = 0;

// Vị trí tích lũy hàng chờ trong Queue
long queued_step_x = 0;
long queued_step_y = 0;
long queued_step_z = 0;

volatile bool is_moving_x = false;
volatile bool is_moving_y = false;
volatile bool is_moving_z = false;
volatile int current_g = 0;
volatile int exact_g = 0;
volatile uint32_t interval_response_ms = 30; // 30ms gửi vị trí 1 lần (khoảng 33Hz cho GUI plot)
volatile long latest_response_time = 0;

// Cờ quản lý trạng thái truyền Serial
volatile bool is_executing = false;     // Đang thực thi lệnh
volatile bool send_finish_flag = false; // Báo hiệu đã hoàn thành toàn bộ lệnh

// Chuỗi bộ đệm đọc Serial bất đồng bộ
String rx_buffer = "";

// 7. Core 0: Motion Controller
// 7. Core 0: Motion Controller
void MotionCore0(void *pvParameters) {
    targetPoint point;
    for (;;) {
        if (xQueueReceive(targetQ, &point, portMAX_DELAY) == pdTRUE) {
            is_executing = true;
            exact_g = point.now_g;

            // 7.1. Lấy điểm bắt đầu thực tế
            long start_x = current_step_x;
            long start_y = current_step_y;
            long start_z = current_step_z;

            // 7.2. Tính khoảng cách bước của từng trục
            long dx = abs(point.x_step - start_x);
            long dy = abs(point.y_step - start_y);
            long dz = abs(point.z_step - start_z);

            // 7.3. Xác định chiều di chuyển
            int sx = (start_x < point.x_step) ? 1 : -1;
            int sy = (start_y < point.y_step) ? 1 : -1;
            int sz = (start_z < point.z_step) ? 1 : -1;

            // 7.4. Xuất tín hiệu DIR
            digitalWrite(PIN_X_DIR, (sx > 0) ? HIGH : LOW);
            digitalWrite(PIN_Y_DIR, (sy > 0) ? HIGH : LOW);
            digitalWrite(PIN_Z_DIR, (sz > 0) ? HIGH : LOW);

            // 7.5. Tìm trục di chuyển nhiều nhất
            long max_step = max(dx, max(dy, dz));

            // 7.6. Bresenham 3D mượt mà
            if (max_step > 0) {
                long error_x = max_step / 2;
                long error_y = max_step / 2;
                long error_z = max_step / 2;

                uint32_t target_delay = point.delay_step_microsec;
                uint32_t start_delay = 1200; // Tốc độ bắt đầu Ramp (us)
                if (start_delay < target_delay) start_delay = target_delay;

                // Tăng/giảm tốc tối đa trong 200 bước đầu/cuối
                long ramp_steps = max_step / 3;
                if (ramp_steps > 200) ramp_steps = 200;

                // Biến theo dõi thời gian nhường CPU xóa Watchdog
                uint32_t last_yield_time = millis();

                for (long i = 0; i < max_step; i++) {
                    bool step_x = false, step_y = false, step_z = false;

                    error_x -= dx;
                    if (error_x < 0) {
                        error_x += max_step;
                        current_step_x += sx;
                        step_x = true;
                    }
                    error_y -= dy;
                    if (error_y < 0) {
                        error_y += max_step;
                        current_step_y += sy;
                        step_y = true;
                    }
                    error_z -= dz;
                    if (error_z < 0) {
                        error_z += max_step;
                        current_step_z += sz;
                        step_z = true;
                    }

                    // Nội suy thời gian trễ cho Ramp-up / Ramp-down
                    uint32_t current_delay = target_delay;
                    if (ramp_steps > 0) {
                        if (i < ramp_steps) {
                            current_delay = start_delay - ((start_delay - target_delay) * i / ramp_steps);
                        } else if (i >= max_step - ramp_steps) {
                            long rem = max_step - 1 - i;
                            current_delay = start_delay - ((start_delay - target_delay) * rem / ramp_steps);
                        }
                    }

                    // Tạo xung HIGH
                    if (step_x) {
                        digitalWrite(PIN_X_STEP, HIGH);
                        is_moving_x = true;
                    }
                    if (step_y){ 
                        digitalWrite(PIN_Y_STEP, HIGH);
                        is_moving_y = true;
                    }
                    if (step_z){
                        digitalWrite(PIN_Z_STEP, HIGH);
                        is_moving_z = true;
                    }

                    delayMicroseconds(3); // Độ rộng xung HIGH

                    // Trả về LOW
                    if (step_x) digitalWrite(PIN_X_STEP, LOW);
                    if (step_y) digitalWrite(PIN_Y_STEP, LOW);
                    if (step_z) digitalWrite(PIN_Z_STEP, LOW);

                    delayMicroseconds(current_delay);

                    // Nhường CPU 1ms cho IDLE0 sau mỗi 200ms để tránh kích hoạt Watchdog khi F quá chậm
                    if (millis() - last_yield_time > 200) {
                        vTaskDelay(1);
                        last_yield_time = millis();
                    }
                }
            }
            is_moving_x = false;  
            is_moving_y = false;  
            is_moving_z = false;  

            // Kiểm tra nếu hàng chờ đã hết lệnh
            if (uxQueueMessagesWaiting(targetQ) == 0) {
                is_executing = false;
                send_finish_flag = true;
            }
        }
    }
}

// 8. Parse and Queue
void Parse_and_Queue(String line) {
    line.trim();
    if (line.length() == 0) return;

    if (line == "PING") {
        Serial.println("PONG");
        Serial.flush();
        return;
    }

    if (line == "reset"){
        ESP.restart();
        return;
    }

    if (line.startsWith("t:")) {
        float resolution_s = line.substring(2).toFloat();
        uint32_t resolution_ms = (uint32_t)(resolution_s * 1000.0f);
        interval_response_ms = (resolution_ms < 10) ? 10 : resolution_ms;
        Serial.println("received_t");
        Serial.flush();
        return;
    }

    String serial_line_upper = line;
    serial_line_upper.toUpperCase();
    if (serial_line_upper.startsWith("G0") || serial_line_upper.startsWith("G1")) {
        current_g = serial_line_upper.startsWith("G0") ? 0 : 1;

        int target_g;
        float target_x_mm = ((float)queued_step_x / STEP_PER_MM_X);
        float target_y_mm = ((float)queued_step_y / STEP_PER_MM_Y);
        float target_z_mm = ((float)queued_step_z / STEP_PER_MM_Z);
        float feedrate = DEFAULT_FR;

        int index_G = serial_line_upper.indexOf('G');
        int index_X = serial_line_upper.indexOf('X');
        int index_Y = serial_line_upper.indexOf('Y');
        int index_Z = serial_line_upper.indexOf('Z');
        int index_F = serial_line_upper.indexOf('F');

        if (index_G != -1) target_g = line.substring(index_G + 1).toInt();
        if (index_X != -1) target_x_mm = line.substring(index_X + 1).toFloat();
        if (index_Y != -1) target_y_mm = line.substring(index_Y + 1).toFloat();
        if (index_Z != -1) target_z_mm = line.substring(index_Z + 1).toFloat();
        if (index_F != -1) feedrate = line.substring(index_F + 1).toFloat();

        targetPoint point;
        point.x_step = lround(target_x_mm * STEP_PER_MM_X);
        point.y_step = lround(target_y_mm * STEP_PER_MM_Y);
        point.z_step = lround(target_z_mm * STEP_PER_MM_Z);
        point.now_g = target_g;
        
        float dx_mm = fabsf(target_x_mm - ((float)queued_step_x / STEP_PER_MM_X));
        float dy_mm = fabsf(target_y_mm - ((float)queued_step_y / STEP_PER_MM_Y));
        float dz_mm = fabsf(target_z_mm - ((float)queued_step_z / STEP_PER_MM_Z));
        float total_dist_mm = sqrtf(dx_mm * dx_mm + dy_mm * dy_mm + dz_mm * dz_mm);

        long dx = abs(point.x_step - queued_step_x);
        long dy = abs(point.y_step - queued_step_y);
        long dz = abs(point.z_step - queued_step_z);
        long max_step = max(dx, max(dy, dz));

        // Cập nhật vị trí tích lũy cho lệnh tiếp theo trong Queue
        queued_step_x = point.x_step;
        queued_step_y = point.y_step;
        queued_step_z = point.z_step;

        if (max_step > 0 && feedrate > 0 && total_dist_mm > 0) {
            float feedrate_mm_s = feedrate / 60.0f;
            float total_time_sec = total_dist_mm / feedrate_mm_s;
            uint32_t calculated_delay = (uint32_t)((total_time_sec * 1000000.0f) / max_step);
            point.delay_step_microsec = max(calculated_delay, (uint32_t)80);
        } else {
            point.delay_step_microsec = 1000;
        }

        // Bật trạng thái đang chạy khi có lệnh mới
        is_executing = true;
        send_finish_flag = false;

        xQueueSend(targetQ, &point, portMAX_DELAY);
        Serial.println("received");
        Serial.flush();
    }
}

// 9. Core 1: Serial Communication (Non-blocking)
void SerialCore1(void *pvParameters) {
    for (;;) {
        // Đọc Serial từng ký tự không gây nghẽn Thread
        while (Serial.available() > 0) {
            char c = Serial.read();
            if (c == '\n') {
                Parse_and_Queue(rx_buffer);
                rx_buffer = "";
            } else if (c != '\r') {
                rx_buffer += c;
            }
        }

        // Chỉ gửi vị trí khi motor đang di chuyển / xử lý lệnh
        if (is_executing) {
            if (millis() - latest_response_time >= interval_response_ms) {
                latest_response_time = millis();
                
                float x_mm = (float)current_step_x / STEP_PER_MM_X;
                float y_mm = (float)current_step_y / STEP_PER_MM_Y;
                float z_mm = (float)current_step_z / STEP_PER_MM_Z;

                Serial.printf("<POS:%d,%.3f,%.3f,%.3f,%s,%s,%s><STEP:%ld,%ld,%ld>\n",
                                exact_g, x_mm, y_mm, z_mm, 
                                is_moving_x ? "run" : "idle", is_moving_y ? "run" : "idle", is_moving_z ? "run" : "idle",
                                current_step_x, current_step_y, current_step_z);
            }
        }

        // Khi hoàn thành toàn bộ lệnh: gửi tọa độ chốt cuối cùng + tín hiệu FINISH
        if (send_finish_flag) {
            send_finish_flag = false;

            float x_mm = (float)current_step_x / STEP_PER_MM_X;
            float y_mm = (float)current_step_y / STEP_PER_MM_Y;
            float z_mm = (float)current_step_z / STEP_PER_MM_Z;

            Serial.printf("<POS:%d,%.3f,%.3f,%.3f,idle,idle,idle><STEP:%ld,%ld,%ld>\n",
                            exact_g, x_mm, y_mm, z_mm, 
                            current_step_x, current_step_y, current_step_z);

            Serial.println("finish");
            Serial.flush();
        }

        vTaskDelay(pdMS_TO_TICKS(2));
    }
}

void setup() {
    Serial.begin(115200);
    rx_buffer.reserve(128);

    pinMode(PIN_X_STEP, OUTPUT);
    pinMode(PIN_X_DIR, OUTPUT);
    pinMode(PIN_Y_STEP, OUTPUT);
    pinMode(PIN_Y_DIR, OUTPUT);
    pinMode(PIN_Z_STEP, OUTPUT);
    pinMode(PIN_Z_DIR, OUTPUT);
    pinMode(PIN_ENABLE, OUTPUT);

    digitalWrite(PIN_ENABLE, LOW); // Enable Driver

    targetQ = xQueueCreate(100, sizeof(targetPoint));

    xTaskCreatePinnedToCore(MotionCore0, "MotionCore0", 8192, NULL, 5, NULL, 0);
    xTaskCreatePinnedToCore(SerialCore1, "SerialCore1", 8192, NULL, 1, NULL, 1);

    vTaskDelay(pdMS_TO_TICKS(5));
}

void loop() {
    vTaskDelete(NULL);
}