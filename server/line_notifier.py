import os
import requests
import json
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

class LineNotifier:
    def __init__(self):
        self.channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
        self.channel_secret = os.getenv('LINE_CHANNEL_SECRET')
        self.enabled = bool(self.channel_access_token)
        
        if not self.enabled:
            logger.warning("LINE Messaging API not configured. Notifications will be disabled.")
        else:
            logger.info("LINE Messaging API configured successfully")
    
    def send_detection_alert(self, device_id: str, person_count: int, timestamp: datetime, confidence_scores: list):
        """人検出アラートを送信"""
        if not self.enabled:
            logger.info(f"[MOCK LINE] Alert: Device={device_id}, Count={person_count}")
            return
        
        # メッセージ作成
        message_text = self._create_alert_message(device_id, person_count, timestamp, confidence_scores)
        
        # Flex Message作成（より見栄えの良い通知）
        flex_message = self._create_flex_message(device_id, person_count, timestamp, confidence_scores)
        
        try:
            # Push APIを使用（実際の運用では適切なuser_idまたはgroup_idが必要）
            # この例では管理者向けのテスト用ID使用
            self._send_push_message("USER_ID_HERE", flex_message)
            logger.info(f"LINE alert sent for device {device_id}")
            
        except Exception as e:
            logger.error(f"Failed to send LINE notification: {e}")
            # フォールバック：シンプルテキストメッセージ
            try:
                self._send_simple_message("USER_ID_HERE", message_text)
            except Exception as e2:
                logger.error(f"Failed to send fallback LINE message: {e2}")
    
    def _create_alert_message(self, device_id: str, person_count: int, timestamp: datetime, confidence_scores: list) -> str:
        """シンプルなテキストメッセージを作成"""
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        
        message = f"""🚨 人検出アラート
デバイス: {device_id}
検出人数: {person_count}人
平均信頼度: {avg_confidence:.2f}
時刻: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}"""
        
        return message
    
    def _create_flex_message(self, device_id: str, person_count: int, timestamp: datetime, confidence_scores: list) -> dict:
        """Flex Messageを作成"""
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        
        flex_message = {
            "type": "flex",
            "altText": f"人検出アラート - {device_id}",
            "contents": {
                "type": "bubble",
                "header": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": "🚨 人検出アラート",
                            "weight": "bold",
                            "color": "#FF4444",
                            "size": "lg"
                        }
                    ],
                    "backgroundColor": "#FFE6E6"
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "baseline",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "デバイス:",
                                    "color": "#666666",
                                    "size": "sm",
                                    "flex": 2
                                },
                                {
                                    "type": "text",
                                    "text": device_id,
                                    "weight": "bold",
                                    "size": "sm",
                                    "flex": 3,
                                    "wrap": True
                                }
                            ],
                            "margin": "md"
                        },
                        {
                            "type": "box",
                            "layout": "baseline",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "検出人数:",
                                    "color": "#666666",
                                    "size": "sm",
                                    "flex": 2
                                },
                                {
                                    "type": "text",
                                    "text": f"{person_count}人",
                                    "weight": "bold",
                                    "size": "sm",
                                    "flex": 3,
                                    "color": "#FF4444"
                                }
                            ],
                            "margin": "md"
                        },
                        {
                            "type": "box",
                            "layout": "baseline",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "信頼度:",
                                    "color": "#666666",
                                    "size": "sm",
                                    "flex": 2
                                },
                                {
                                    "type": "text",
                                    "text": f"{avg_confidence:.1%}",
                                    "weight": "bold",
                                    "size": "sm",
                                    "flex": 3
                                }
                            ],
                            "margin": "md"
                        },
                        {
                            "type": "box",
                            "layout": "baseline",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "時刻:",
                                    "color": "#666666",
                                    "size": "sm",
                                    "flex": 2
                                },
                                {
                                    "type": "text",
                                    "text": timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                                    "size": "sm",
                                    "flex": 3,
                                    "wrap": True
                                }
                            ],
                            "margin": "md"
                        }
                    ]
                }
            }
        }
        
        return flex_message
    
    def _send_push_message(self, to: str, message: dict):
        """Push APIでメッセージ送信"""
        url = "https://api.line.me/v2/bot/message/push"
        
        headers = {
            "Authorization": f"Bearer {self.channel_access_token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "to": to,
            "messages": [message]
        }
        
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
    
    def _send_simple_message(self, to: str, text: str):
        """シンプルテキストメッセージ送信"""
        url = "https://api.line.me/v2/bot/message/push"
        
        headers = {
            "Authorization": f"Bearer {self.channel_access_token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "to": to,
            "messages": [
                {
                    "type": "text",
                    "text": text
                }
            ]
        }
        
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
    
    def send_system_status(self, message: str):
        """システム状態通知"""
        if not self.enabled:
            logger.info(f"[MOCK LINE] System: {message}")
            return
        
        try:
            self._send_simple_message("USER_ID_HERE", f"🔧 システム通知: {message}")
            logger.info("System status notification sent")
        except Exception as e:
            logger.error(f"Failed to send system notification: {e}")

# グローバルインスタンス
line_notifier = LineNotifier()
