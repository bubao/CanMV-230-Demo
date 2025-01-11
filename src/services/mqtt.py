import json
from libs.umqtt.simple import MQTTClient
from src.services.utils import logging

LOGNAME = "mqtt"


class MQTTPublish:
    def __init__(self, config):
        self.broker = config["broker"]
        self.port = config["port"]
        self.topic_detection = config["topic_detection"]
        self.client_id = config.get("client_id", "yolo_client")
        self.username = config.get("username", None)
        self.password = config.get("password", None)

        # 初始化 MQTTClient
        self.client = MQTTClient(self.client_id, self.broker, port=self.port)

        # 如果提供了用户名和密码，设置它们
        if self.username and self.password:
            self.client.set_callback(self.on_message)
            self.client.set_last_will(
                topic=self.topic_detection, msg="Disconnected", retain=True
            )

        # 初始化连接状态
        self.is_connected = False

    def connect(self):
        """连接到 MQTT 代理服务器"""
        try:
            # 连接到 MQTT 代理服务器
            self.client.connect()
            self.is_connected = True
            logging(f"Connected to MQTT broker: {self.broker}", log_name=LOGNAME)
            return True
        except Exception as e:
            logging(f"Error connecting to MQTT broker: {e}", log_name=LOGNAME)
            return False

    def publish(self, topic, message):
        """发布消息到指定的主题"""
        if not self.is_connected:
            # logging(
            #     f"MQTT not connected. Unable to publish to {topic}", log_name=LOGNAME
            # )
            return

        try:
            # 发布消息，umqtt.simple 采用的是 publish(topic, msg)
            self.client.publish(topic, message)
            logging(f"Message published to {topic}", log_name=LOGNAME)
        except Exception as e:
            logging(f"Error publishing message to {topic}: {e}", log_name=LOGNAME)

    def subscribe(self, topic):
        """订阅一个 MQTT 主题"""
        if not self.is_connected:
            logging(
                f"MQTT not connected. Unable to subscribe to {topic}", log_name=LOGNAME
            )
            return

        try:
            # 订阅主题，umqtt.simple 采用的是 subscribe(topic)
            self.client.subscribe(topic)
            logging(f"Subscribed to topic: {topic}", log_name=LOGNAME)
        except Exception as e:
            logging(f"Error subscribing to {topic}: {e}", log_name=LOGNAME)

    def unsubscribe(self, topic):
        """取消订阅一个 MQTT 主题"""
        if not self.is_connected:
            logging(
                f"MQTT not connected. Unable to unsubscribe from {topic}",
                log_name=LOGNAME,
            )
            return

        try:
            # 取消订阅主题，umqtt.simple 采用的是 unsubscribe(topic)
            self.client.unsubscribe(topic)
            logging(f"Unsubscribed from topic: {topic}", log_name=LOGNAME)
        except Exception as e:
            logging(f"Error unsubscribing from {topic}: {e}", log_name=LOGNAME)

    def disconnect(self):
        """断开 MQTT 连接"""
        if self.is_connected:
            self.client.disconnect()
            self.is_connected = False
            logging("Disconnected from MQTT broker", log_name=LOGNAME)
        else:
            logging("MQTT not connected. Unable to disconnect.", log_name=LOGNAME)

    def loop(self):
        """执行 MQTT 客户端的循环，保持与代理的连接"""
        try:
            self.client.wait_msg()  # 阻塞，等待消息
        except Exception as e:
            logging(f"Error in MQTT loop: {e}", log_name=LOGNAME)

    def on_message(self, topic, msg):
        """收到消息时的回调函数"""
        logging(f"Received message: {msg} on topic: {topic}", log_name=LOGNAME)
