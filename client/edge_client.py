"""
エッジデバイス側のクライアントアプリケーション
カメラからの画像をサーバに送信する
"""

import cv2
import time
import requests
import argparse
import uuid
from datetime import datetime
from pathlib import Path
import json
import os
from typing import Optional


class EdgeClient:
    """エッジデバイス用クライアント"""
    
    def __init__(
        self,
        server_url: str,
        device_id: str,
        api_key: Optional[str] = None,
        camera_id: int = 0,
        fps: float = 1.0,
        image_width: int = 640,
        image_height: int = 360,
        jpeg_quality: int = 80
    ):
        self.server_url = server_url.rstrip('/')
        self.device_id = device_id
        self.api_key = api_key
        self.camera_id = camera_id
        self.fps = fps
        self.image_width = image_width
        self.image_height = image_height
        self.jpeg_quality = jpeg_quality
        
        # 統計情報
        self.stats = {
            "total_sent": 0,
            "success_count": 0,
            "error_count": 0,
            "start_time": None,
            "last_success": None,
            "last_error": None
        }
        
        # カメラの初期化
        self.cap = None
        self._init_camera()
    
    def _init_camera(self):
        """カメラの初期化"""
        try:
            self.cap = cv2.VideoCapture(self.camera_id)
            
            if not self.cap.isOpened():
                raise RuntimeError(f"カメラ {self.camera_id} を開けません")
            
            # カメラ設定
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.image_width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.image_height)
            self.cap.set(cv2.CAP_PROP_FPS, 30)  # カメラのFPSは高めに設定
            
            print(f"✅ カメラ初期化成功: {self.camera_id}")
            print(f"   解像度: {self.image_width}x{self.image_height}")
            print(f"   送信FPS: {self.fps}")
            
        except Exception as e:
            print(f"❌ カメラ初期化失敗: {e}")
            self.cap = None
    
    def capture_frame(self) -> Optional[bytes]:
        """フレームをキャプチャしてJPEG形式で返す"""
        if self.cap is None:
            return None
        
        try:
            ret, frame = self.cap.read()
            if not ret:
                print("⚠️ フレーム取得失敗")
                return None
            
            # リサイズ
            frame_resized = cv2.resize(frame, (self.image_width, self.image_height))
            
            # JPEG エンコード
            encode_params = [cv2.IMWRITE_JPEG_QUALITY, self.jpeg_quality]
            success, encoded_img = cv2.imencode('.jpg', frame_resized, encode_params)
            
            if not success:
                print("⚠️ JPEG エンコード失敗")
                return None
            
            return encoded_img.tobytes()
            
        except Exception as e:
            print(f"❌ フレームキャプチャエラー: {e}")
            return None
    
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
                self.stats["last_success"] = datetime.now()
                
                print(f"✅ 送信成功: {result.get('event_id', 'N/A')} "
                      f"(人数: {result.get('person_count', 0)}, "
                      f"異常: {result.get('anomaly_detected', False)})")
                return True
            else:
                print(f"❌ 送信失敗: HTTP {response.status_code} - {response.text}")
                self.stats["error_count"] += 1
                self.stats["last_error"] = datetime.now()
                return False
                
        except requests.exceptions.Timeout:
            print("❌ 送信タイムアウト")
            self.stats["error_count"] += 1
            self.stats["last_error"] = datetime.now()
            return False
        except requests.exceptions.ConnectionError:
            print("❌ サーバー接続エラー")
            self.stats["error_count"] += 1
            self.stats["last_error"] = datetime.now()
            return False
        except Exception as e:
            print(f"❌ 送信エラー: {e}")
            self.stats["error_count"] += 1
            self.stats["last_error"] = datetime.now()
            return False
    
    def run(self):
        """メインループ実行"""
        print(f"🚀 Edge Client 開始")
        print(f"   デバイスID: {self.device_id}")
        print(f"   サーバーURL: {self.server_url}")
        print(f"   FPS: {self.fps}")
        print()
        
        if self.cap is None:
            print("❌ カメラが初期化されていません")
            return
        
        self.stats["start_time"] = datetime.now()
        frame_interval = 1.0 / self.fps
        
        try:
            while True:
                start_time = time.time()
                
                # フレームキャプチャ
                image_data = self.capture_frame()
                
                if image_data:
                    # サーバに送信
                    self.send_frame(image_data)
                    self.stats["total_sent"] += 1
                    
                    # 統計表示（10回ごと）
                    if self.stats["total_sent"] % 10 == 0:
                        self.print_stats()
                
                # FPS調整のための待機
                elapsed = time.time() - start_time
                sleep_time = max(0, frame_interval - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                
        except KeyboardInterrupt:
            print("\n🛑 停止要求を受信")
        except Exception as e:
            print(f"❌ 実行エラー: {e}")
        finally:
            self.cleanup()
    
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
    
    def cleanup(self):
        """リソースのクリーンアップ"""
        if self.cap:
            self.cap.release()
            print("📹 カメラを解放しました")
        
        # 最終統計
        self.print_stats()


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description="Edge Anomaly Detection Client")
    
    parser.add_argument("--server", default="http://localhost:8000",
                       help="サーバーURL (default: http://localhost:8000)")
    parser.add_argument("--device-id", default=f"jetson-{uuid.uuid4().hex[:6]}",
                       help="デバイスID (default: 自動生成)")
    parser.add_argument("--api-key", default=None,
                       help="API キー")
    parser.add_argument("--camera", type=int, default=0,
                       help="カメラデバイスID (default: 0)")
    parser.add_argument("--fps", type=float, default=1.0,
                       help="送信フレームレート (default: 1.0)")
    parser.add_argument("--width", type=int, default=640,
                       help="画像幅 (default: 640)")
    parser.add_argument("--height", type=int, default=360,
                       help="画像高さ (default: 360)")
    parser.add_argument("--quality", type=int, default=80,
                       help="JPEG品質 (default: 80)")
    parser.add_argument("--config", default=None,
                       help="設定ファイルパス (JSON)")
    
    args = parser.parse_args()
    
    # 設定ファイルから読み込み
    config = {}
    if args.config and Path(args.config).exists():
        with open(args.config, 'r') as f:
            config = json.load(f)
    
    # 設定の統合（コマンドライン引数が優先）
    client_config = {
        "server_url": config.get("server_url", args.server),
        "device_id": config.get("device_id", args.device_id),
        "api_key": config.get("api_key", args.api_key),
        "camera_id": config.get("camera_id", args.camera),
        "fps": config.get("fps", args.fps),
        "image_width": config.get("image_width", args.width),
        "image_height": config.get("image_height", args.height),
        "jpeg_quality": config.get("jpeg_quality", args.quality)
    }
    
    # クライアント実行
    client = EdgeClient(**client_config)
    client.run()


if __name__ == "__main__":
    main()
