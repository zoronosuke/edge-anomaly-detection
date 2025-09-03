"""
LINE通知システム
"""

import os
import asyncio
from typing import Optional
from linebot.v3 import WebhookHandler
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, PushMessageRequest, TextMessage
from linebot.v3.exceptions import InvalidSignatureError


class LineNotifier:
    """LINE Bot APIを使用した通知システム"""
    
    def __init__(self):
        self.channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
        self.channel_secret = os.getenv("LINE_CHANNEL_SECRET")
        self.user_id = os.getenv("LINE_USER_ID")  # 通知先のユーザーID
        
        self.api_client = None
        self.messaging_api = None
        
        if self.channel_access_token and self.channel_secret:
            try:
                configuration = Configuration(access_token=self.channel_access_token)
                self.api_client = ApiClient(configuration)
                self.messaging_api = MessagingApi(self.api_client)
                print("✅ LINE Bot API 初期化成功")
            except Exception as e:
                print(f"⚠️ LINE Bot API 初期化失敗: {e}")
        else:
            print("⚠️ LINE Bot の認証情報が設定されていません")
    
    def is_enabled(self) -> bool:
        """LINE通知が有効かどうか"""
        return (
            self.messaging_api is not None and 
            self.channel_access_token is not None and
            self.user_id is not None
        )
    
    async def send_message(self, message: str, user_id: Optional[str] = None) -> bool:
        """
        LINEメッセージを送信
        
        Args:
            message: 送信するメッセージ
            user_id: 送信先ユーザーID（省略時は環境変数から取得）
            
        Returns:
            送信成功かどうか
        """
        if not self.is_enabled():
            print("⚠️ LINE通知が無効です")
            return False
        
        target_user_id = user_id or self.user_id
        if not target_user_id:
            print("⚠️ 送信先ユーザーIDが設定されていません")
            return False
        
        try:
            # メッセージオブジェクトの作成
            text_message = TextMessage(text=message)
            request = PushMessageRequest(
                to=target_user_id,
                messages=[text_message]
            )
            
            # メッセージ送信（非同期）
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self.messaging_api.push_message(request)
            )
            
            print(f"📱 LINE通知送信成功: {target_user_id}")
            return True
            
        except Exception as e:
            print(f"❌ LINE通知送信失敗: {e}")
            return False
    
    async def send_rich_message(
        self, 
        title: str,
        content: str,
        details: Optional[dict] = None,
        user_id: Optional[str] = None
    ) -> bool:
        """
        リッチメッセージ（Flex Message）を送信
        
        Args:
            title: メッセージタイトル
            content: メッセージ内容
            details: 詳細情報
            user_id: 送信先ユーザーID
            
        Returns:
            送信成功かどうか
        """
        # シンプルなテキストメッセージとして送信
        message_parts = [f"🚨 {title}", f"📍 {content}"]
        
        if details:
            for key, value in details.items():
                message_parts.append(f"• {key}: {value}")
        
        message = "\n".join(message_parts)
        return await self.send_message(message, user_id)
