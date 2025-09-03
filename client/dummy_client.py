"""
テスト用のダミークライアント
実際のカメラなしでテスト画像を送信
"""

import time
import requests
import argparse
import uuid
import random
from datetime import datetime
from pathlib import Path
import json
import numpy as np
import cv2
from typing import Optional


class DummyEdgeClient:
    """テスト用ダミークライアント"""
    
    def __init__(
        self,
        server_url: str,
        device_id: str,
        api_key: Optional[str] = None,
        fps: float = 1.0,
        image_width: int = 640,
        image_height: int = 360,
        jpeg_quality: int = 80,
        simulate_person: bool = True
    ):
        self.server_url = server_url.rstrip('/')
        self.device_id = device_id
        self.api_key = api_key
        self.fps = fps
        self.image_width = image_width
        self.image_height = image_height
        self.jpeg_quality = jpeg_quality
        self.simulate_person = simulate_person
        
        # 統計情報
        self.stats = {
            "total_sent": 0,
            "success_count": 0,
            "error_count": 0,
            "start_time": None
        }
    
    def generate_test_image(self) -> bytes:
        """テスト用画像を生成"""
        # ランダムな背景色で画像を作成
        bg_color = (
            random.randint(50, 200),
            random.randint(50, 200),
            random.randint(50, 200)
        )
        
        image = np.full(
            (self.image_height, self.image_width, 3),
            bg_color,
            dtype=np.uint8
        )
        
        # テキストを描画
        text = f"Device: {self.device_id}"
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(
            image, text, (10, 30),
            font, 0.7, (255, 255, 255), 2
        )
        
        # タイムスタンプを描画
        timestamp = datetime.now().strftime("%H:%M:%S")
        cv2.putText(
            image, timestamp, (10, 60),
            font, 0.6, (255, 255, 255), 2
        )
        
        # 人のような矩形を描画（シミュレーション）
        if self.simulate_person and random.random() < 0.3:  # 30%の確率で人を描画
            num_persons = random.randint(1, 3)
            for i in range(num_persons):
                x = random.randint(100, self.image_width - 150)
                y = random.randint(100, self.image_height - 200)
                w = random.randint(50, 100)
                h = random.randint(100, 150)
                
                # 人を表す矩形
                cv2.rectangle(
                    image, (x, y), (x + w, y + h),
                    (0, 255, 0), 3
                )
                cv2.putText(
                    image, f"Person {i+1}", (x, y-10),
                    font, 0.5, (0, 255, 0), 2
                )
        
        # フレーム番号を描画
        frame_text = f"Frame: {self.stats['total_sent'] + 1}"
        cv2.putText(
            image, frame_text, (10, self.image_height - 20),
            font, 0.5, (255, 255, 255), 1
        )
        
        # JPEG エンコード
        encode_params = [cv2.IMWRITE_JPEG_QUALITY, self.jpeg_quality]
        success, encoded_img = cv2.imencode('.jpg', image, encode_params)
        
        if success:
            return encoded_img.tobytes()
        else:
            raise RuntimeError("JPEG エンコードに失敗")
    
    def send_frame(self, image_data: bytes) -> bool:
        """フレームをサーバに送信"""
        try:
            url = f"{self.server_url}/ingest"
            
            # タイムスタンプ
            timestamp = datetime.now().isoformat()
            
            # ファイルデータ
            files = {
                'file': ('image.jpg', image_data, 'image/jpeg')
            }
            
            # フォームデータ
            data = {
                'device_id': self.device_id,
                'ts': timestamp
            }
            
            # ヘッダー
            headers = {}
            if self.api_key:
                headers['X-Api-Key'] = self.api_key
            
            # HTTP POST 送信
            response = requests.post(
                url,
                files=files,
                data=data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                self.stats["success_count"] += 1
                
                print(f"✅ 送信成功: {result.get('event_id', 'N/A')} "
                      f"(人数: {result.get('person_count', 0)}, "
                      f"異常: {result.get('anomaly_detected', False)})")
                return True
            else:
                print(f"❌ 送信失敗: HTTP {response.status_code} - {response.text}")
                self.stats["error_count"] += 1
                return False
                
        except Exception as e:
            print(f"❌ 送信エラー: {e}")
            self.stats["error_count"] += 1
            return False
    
    def run(self, duration_seconds: Optional[int] = None):
        """メインループ実行"""
        print(f"🧪 Dummy Edge Client 開始")
        print(f"   デバイスID: {self.device_id}")
        print(f"   サーバーURL: {self.server_url}")
        print(f"   FPS: {self.fps}")
        print(f"   人シミュレーション: {self.simulate_person}")
        if duration_seconds:
            print(f"   実行時間: {duration_seconds}秒")
        print()
        
        self.stats["start_time"] = datetime.now()
        frame_interval = 1.0 / self.fps
        start_time = time.time()
        
        try:
            while True:
                loop_start = time.time()
                
                # テスト画像生成
                image_data = self.generate_test_image()
                
                # サーバに送信
                self.send_frame(image_data)
                self.stats["total_sent"] += 1
                
                # 統計表示（10回ごと）
                if self.stats["total_sent"] % 10 == 0:
                    self.print_stats()
                
                # 実行時間チェック
                if duration_seconds and (time.time() - start_time) >= duration_seconds:
                    print(f"\n⏰ 指定時間（{duration_seconds}秒）が経過しました")
                    break
                
                # FPS調整のための待機
                elapsed = time.time() - loop_start
                sleep_time = max(0, frame_interval - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                
        except KeyboardInterrupt:
            print("\n🛑 停止要求を受信")
        finally:
            self.print_final_stats()
    
    def print_stats(self):
        """統計情報を表示"""
        now = datetime.now()
        if self.stats["start_time"]:
            elapsed = (now - self.stats["start_time"]).total_seconds()
            rate = self.stats["total_sent"] / elapsed if elapsed > 0 else 0
            
            print(f"📊 統計: 送信 {self.stats['total_sent']} "
                  f"(成功: {self.stats['success_count']}, "
                  f"失敗: {self.stats['error_count']}, "
                  f"レート: {rate:.2f} fps)")
    
    def print_final_stats(self):
        """最終統計を表示"""
        print("\n" + "="*50)
        print("📊 最終統計")
        print("="*50)
        self.print_stats()
        
        if self.stats["total_sent"] > 0:
            success_rate = (self.stats["success_count"] / self.stats["total_sent"]) * 100
            print(f"📈 成功率: {success_rate:.2f}%")
        
        if self.stats["start_time"]:
            total_time = (datetime.now() - self.stats["start_time"]).total_seconds()
            print(f"⏱️ 総実行時間: {total_time:.2f}秒")


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description="Dummy Edge Anomaly Detection Client")
    
    parser.add_argument("--server", default="http://localhost:8000",
                       help="サーバーURL")
    parser.add_argument("--device-id", default=f"dummy-{uuid.uuid4().hex[:6]}",
                       help="デバイスID")
    parser.add_argument("--api-key", default=None,
                       help="API キー")
    parser.add_argument("--fps", type=float, default=1.0,
                       help="送信フレームレート")
    parser.add_argument("--width", type=int, default=640,
                       help="画像幅")
    parser.add_argument("--height", type=int, default=360,
                       help="画像高さ")
    parser.add_argument("--quality", type=int, default=80,
                       help="JPEG品質")
    parser.add_argument("--duration", type=int, default=None,
                       help="実行時間（秒）")
    parser.add_argument("--no-person", action="store_true",
                       help="人のシミュレーションを無効化")
    
    args = parser.parse_args()
    
    # クライアント実行
    client = DummyEdgeClient(
        server_url=args.server,
        device_id=args.device_id,
        api_key=args.api_key,
        fps=args.fps,
        image_width=args.width,
        image_height=args.height,
        jpeg_quality=args.quality,
        simulate_person=not args.no_person
    )
    
    client.run(duration_seconds=args.duration)


if __name__ == "__main__":
    main()
