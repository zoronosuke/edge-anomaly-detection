import os
import time
import requests
import cv2
import json
from datetime import datetime
from pathlib import Path
import logging
import argparse

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EdgeClient:
    def __init__(self, device_id: str, server_url: str, api_key: str):
        self.device_id = device_id
        self.server_url = server_url.rstrip('/')
        self.api_key = api_key
        self.camera = None
        self.capture_width = 640
        self.capture_height = 360
        self.jpeg_quality = 80
        self.fps = 1  # 1秒ごとに1フレーム
        
        logger.info(f"EdgeClient initialized: device_id={device_id}")
    
    def init_camera(self, camera_index: int = 0):
        """カメラを初期化"""
        try:
            self.camera = cv2.VideoCapture(camera_index)
            if not self.camera.isOpened():
                raise Exception(f"Cannot open camera {camera_index}")
            
            # カメラ設定
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.capture_width)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.capture_height)
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            
            logger.info(f"Camera {camera_index} initialized successfully")
            return True
        
        except Exception as e:
            logger.error(f"Failed to initialize camera: {e}")
            return False
    
    def capture_frame(self) -> bytes:
        """フレームをキャプチャしてJPEGにエンコード"""
        if not self.camera:
            raise Exception("Camera not initialized")
        
        ret, frame = self.camera.read()
        if not ret:
            raise Exception("Failed to capture frame")
        
        # リサイズ
        frame = cv2.resize(frame, (self.capture_width, self.capture_height))
        
        # JPEG圧縮
        encode_param = [cv2.IMWRITE_JPEG_QUALITY, self.jpeg_quality]
        _, encoded_img = cv2.imencode('.jpg', frame, encode_param)
        
        return encoded_img.tobytes()
    
    def send_image(self, image_data: bytes) -> dict:
        """画像をサーバに送信"""
        url = f"{self.server_url}/ingest"
        
        # リクエストデータの準備
        timestamp = datetime.now().isoformat()
        
        files = {
            'file': ('image.jpg', image_data, 'image/jpeg')
        }
        
        data = {
            'device_id': self.device_id,
            'ts': timestamp
        }
        
        headers = {
            'Authorization': f'Bearer {self.api_key}'
        }
        
        try:
            response = requests.post(url, files=files, data=data, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send image: {e}")
            raise
    
    def run_continuous(self):
        """連続実行モード"""
        logger.info("Starting continuous capture mode...")
        
        if not self.init_camera():
            return
        
        try:
            while True:
                start_time = time.time()
                
                try:
                    # フレームキャプチャ
                    image_data = self.capture_frame()
                    
                    # サーバに送信
                    result = self.send_image(image_data)
                    
                    # ログ出力
                    person_count = result.get('person_count', 0)
                    anomaly = result.get('anomaly_detected', False)
                    processing_time = result.get('processing_time_ms', 0)
                    
                    logger.info(f"Sent frame: persons={person_count}, anomaly={anomaly}, processing_time={processing_time:.1f}ms")
                    
                except Exception as e:
                    logger.error(f"Error in capture/send cycle: {e}")
                
                # 1秒間隔を維持
                elapsed = time.time() - start_time
                sleep_time = max(0, 1.0 - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)
        
        except KeyboardInterrupt:
            logger.info("Stopping capture...")
        
        finally:
            if self.camera:
                self.camera.release()
                logger.info("Camera released")
    
    def send_test_image(self, image_path: str):
        """テスト用：指定した画像ファイルを送信"""
        if not Path(image_path).exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        result = self.send_image(image_data)
        
        print(f"Test image sent successfully:")
        print(f"  Person count: {result.get('person_count', 0)}")
        print(f"  Anomaly detected: {result.get('anomaly_detected', False)}")
        print(f"  Processing time: {result.get('processing_time_ms', 0):.1f}ms")
        print(f"  Event ID: {result.get('event_id', 'N/A')}")
        
        return result

def main():
    parser = argparse.ArgumentParser(description='Edge Device Client')
    parser.add_argument('--device-id', required=True, help='Device ID (e.g., jetson-001)')
    parser.add_argument('--server-url', default='http://localhost:8000', help='Server URL')
    parser.add_argument('--api-key', default='your_api_key_here', help='API Key')
    parser.add_argument('--camera-index', type=int, default=0, help='Camera index')
    parser.add_argument('--test-image', help='Path to test image file')
    parser.add_argument('--mode', choices=['continuous', 'test'], default='continuous', help='Running mode')
    
    args = parser.parse_args()
    
    client = EdgeClient(args.device_id, args.server_url, args.api_key)
    
    if args.mode == 'test' and args.test_image:
        client.send_test_image(args.test_image)
    elif args.mode == 'continuous':
        client.run_continuous()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
