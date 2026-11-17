/*
 * esp32_base.ino — Physical ESP32 micro-ROS firmware (micro_ros_arduino + rclc).
 *
 * Pair with the official host agent on Ubuntu 22.04 + ROS 2 Humble:
 *   ros2 run micro_ros_agent micro_ros_agent serial --dev /dev/ttyUSB0 -b 115200
 *
 * Creates node /esp32_base, subscribes to /cmd_vel (geometry_msgs/msg/Twist),
 * publishes /esp32/status (std_msgs/msg/String), and cuts wheel outputs to zero
 * if /cmd_vel goes silent for 250 ms.
 */

#include <Arduino.h>
#include <micro_ros_arduino.h>

#include <rcl/rcl.h>
#include <rclc/executor.h>
#include <rclc/rclc.h>
#include <rmw_microros/rmw_microros.h>

#include <geometry_msgs/msg/twist.h>
#include <std_msgs/msg/string.h>

#define WHEEL_BASE_M   0.30f
#define WATCHDOG_MS    250UL

static rcl_allocator_t allocator;
static rclc_support_t support;
static rcl_node_t node;
static rcl_subscription_t cmd_sub;
static rcl_publisher_t status_pub;
static rclc_executor_t executor;

static geometry_msgs__msg__Twist cmd_msg;
static std_msgs__msg__String status_msg;
static char status_buf[160];

static uint32_t cmd_rx = 0;
static unsigned long last_cmd_ms = 0;
static bool driving = false;

static void publish_status(const char *state, float vx, float wz, float left, float right) {
  int n = snprintf(
    status_buf, sizeof(status_buf),
    "state=%s cmd_rx=%lu vx=%.3f wz=%.3f left=%.3f right=%.3f",
    state, (unsigned long)cmd_rx, vx, wz, left, right
  );
  status_msg.data.data = status_buf;
  status_msg.data.size = (size_t)(n > 0 ? n : 0);
  status_msg.data.capacity = sizeof(status_buf);
  (void)rcl_publish(&status_pub, &status_msg, NULL);
}

static void on_cmd_vel(const void *msgin) {
  const geometry_msgs__msg__Twist *msg = (const geometry_msgs__msg__Twist *)msgin;
  float vx = (float)msg->linear.x;
  float wz = (float)msg->angular.z;
  float left = vx - 0.5f * wz * WHEEL_BASE_M;
  float right = vx + 0.5f * wz * WHEEL_BASE_M;
  cmd_rx += 1;
  last_cmd_ms = millis();
  driving = true;
  publish_status("DRIVING", vx, wz, left, right);
}

void setup() {
  set_microros_transports();
  while (rmw_uros_ping_agent(100, 1) != RMW_RET_OK) {
    delay(250);
  }

  allocator = rcl_get_default_allocator();
  rclc_support_init(&support, 0, NULL, &allocator);
  rclc_node_init_default(&node, "esp32_base", "", &support);
  rclc_subscription_init_default(
    &cmd_sub, &node,
    ROSIDL_GET_MSG_TYPE_SUPPORT(geometry_msgs, msg, Twist),
    "/cmd_vel"
  );
  rclc_publisher_init_default(
    &status_pub, &node,
    ROSIDL_GET_MSG_TYPE_SUPPORT(std_msgs, msg, String),
    "/esp32/status"
  );
  rclc_executor_init(&executor, &support.context, 1, &allocator);
  rclc_executor_add_subscription(&executor, &cmd_sub, &cmd_msg, &on_cmd_vel, ON_NEW_DATA);
  publish_status("IDLE", 0.0f, 0.0f, 0.0f, 0.0f);
}

void loop() {
  rclc_executor_spin_some(&executor, RCL_MS_TO_NS(10));
  if (driving && (millis() - last_cmd_ms) >= WATCHDOG_MS) {
    driving = false;
    publish_status("WATCHDOG_STOP", 0.0f, 0.0f, 0.0f, 0.0f);
  }
}
