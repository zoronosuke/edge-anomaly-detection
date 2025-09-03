import os
import json
import csv
import uuid
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional
import logging

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from ultralytics import YOLO
import cv2
import numpy as np
from PIL import Image
import aiofiles
# from line_notifier import line_notifier

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/server.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Edge Anomaly Detection Server", version="1.0.0")

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# セキュリティ
security = HTTPBearer()

class DetectionSystem:
    def __init__(self):
        self.model = None
        self.last_alert_at: Dict[str, datetime] = {}
        self.last_event_sig: Dict[str, str] = {}
        self.cooldown_seconds = int(os.getenv('COOLDOWN_SECONDS', 30))
        self.threshold = float(os.getenv('PERSON_DETECTION_THRESHOLD', 0.5))
        self.data_dir = Path(os.getenv('DATA_DIR', './data'))
        self.data_dir.mkdir(exist_ok=True)
        
        # CSVファイルの初期化
        self.events_csv = self.data_dir / 'events.csv'
        self.performance_csv = self.data_dir / 'performance_metrics.csv'
        self._init_csv_files()
        
        logger.info("DetectionSystem initialized")
    
    def _init_csv_files(self):
        """CSVファイルのヘッダーを初期化"""
        if not self.events_csv.exists():
            with open(self.events_csv, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'event_id', 'device_id', 'timestamp', 'person_count', 
                    'anomaly_flag', 'confidence_scores', 'processing_time_ms',
                    'image_filename'
                ])
        
        if not self.performance_csv.exists():
            with open(self.performance_csv, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'device_id', 'request_size_bytes', 
                    'processing_time_ms', 'inference_time_ms', 'total_response_time_ms'
                ])
    
    async def load_model(self):
        """YOLOモデルを読み込み"""
        if self.model is None:
            logger.info("Loading YOLOv8n model...")
            self.model = YOLO('yolov8n.pt')
            logger.info("Model loaded successfully")
    
    def detect_persons(self, image: np.ndarray) -> tuple:
        """人物検出を実行"""
        start_time = datetime.now()
        
        results = self.model(image, conf=self.threshold)
        
        # 人物クラス（class_id=0）のみを抽出
        person_detections = []
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    class_id = int(box.cls[0])
                    if class_id == 0:  # person class
                        confidence = float(box.conf[0])
                        person_detections.append(confidence)
        
        inference_time = (datetime.now() - start_time).total_seconds() * 1000
        return person_detections, inference_time
    
    def should_send_alert(self, device_id: str, person_count: int) -> bool:
        """アラートを送信すべきかチェック"""
        now = datetime.now()
        
        # クールダウンチェック
        if device_id in self.last_alert_at:
            time_diff = now - self.last_alert_at[device_id]
            if time_diff.total_seconds() < self.cooldown_seconds:
                return False
        
        # イベント重複チェック（同じ人数の検出は重複とみなす）
        event_sig = f"{person_count}"
        if device_id in self.last_event_sig:
            if self.last_event_sig[device_id] == event_sig:
                return False
        
        return person_count > 0
    
    async def save_event(self, event_data: dict):
        """イベントをCSVに保存"""
        async with aiofiles.open(self.events_csv, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            await f.write(','.join([
                str(event_data['event_id']),
                str(event_data['device_id']),
                str(event_data['timestamp']),
                str(event_data['person_count']),
                str(event_data['anomaly_flag']),
                str(event_data['confidence_scores']),
                str(event_data['processing_time_ms']),
                str(event_data['image_filename'])
            ]) + '\n')
    
    async def save_performance_metrics(self, metrics: dict):
        """パフォーマンスメトリクスをCSVに保存"""
        async with aiofiles.open(self.performance_csv, 'a', newline='', encoding='utf-8') as f:
            await f.write(','.join([
                str(metrics['timestamp']),
                str(metrics['device_id']),
                str(metrics['request_size_bytes']),
                str(metrics['processing_time_ms']),
                str(metrics['inference_time_ms']),
                str(metrics['total_response_time_ms'])
            ]) + '\n')

# グローバルインスタンス
detection_system = DetectionSystem()

async def verify_api_key(credentials: HTTPAuthorizationCredentials = Security(security)):
    """API キーの検証"""
    expected_key = os.getenv('API_KEY', 'your_api_key_here')
    if credentials.credentials != expected_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return credentials.credentials

@app.on_event("startup")
async def startup_event():
    """アプリケーション起動時の処理"""
    await detection_system.load_model()
    logger.info("Server startup completed")

@app.get("/")
async def root():
    """ヘルスチェック"""
    return {"status": "ok", "message": "Edge Anomaly Detection Server"}

@app.post("/ingest")
async def ingest_image(
    file: UploadFile = File(...),
    device_id: str = Form(...),
    ts: Optional[str] = Form(None),
    api_key: str = Depends(verify_api_key)
):
    """画像を受信して人物検出を実行"""
    start_time = datetime.now()
    
    try:
        # タイムスタンプの処理
        if ts:
            timestamp = datetime.fromisoformat(ts.replace('Z', '+00:00'))
        else:
            timestamp = start_time
        
        # 画像の読み込み
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise HTTPException(status_code=400, detail="Invalid image format")
        
        # 人物検出
        person_detections, inference_time = detection_system.detect_persons(image)
        person_count = len(person_detections)
        
        # アラート判定
        should_alert = detection_system.should_send_alert(device_id, person_count)
        
        if should_alert:
            detection_system.last_alert_at[device_id] = start_time
            detection_system.last_event_sig[device_id] = str(person_count)
        
        # 画像保存（人が検出された場合のみ）
        image_filename = None
        if person_count > 0:
            image_filename = f"{device_id}_{timestamp.strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.jpg"
            image_path = detection_system.data_dir / image_filename
            cv2.imwrite(str(image_path), image)
        
        # イベント保存
        event_id = str(uuid.uuid4())
        event_data = {
            'event_id': event_id,
            'device_id': device_id,
            'timestamp': timestamp.isoformat(),
            'person_count': person_count,
            'anomaly_flag': should_alert,
            'confidence_scores': json.dumps(person_detections),
            'processing_time_ms': inference_time,
            'image_filename': image_filename or ''
        }
        
        await detection_system.save_event(event_data)
        
        # パフォーマンスメトリクス保存
        total_time = (datetime.now() - start_time).total_seconds() * 1000
        metrics = {
            'timestamp': start_time.isoformat(),
            'device_id': device_id,
            'request_size_bytes': len(contents),
            'processing_time_ms': total_time,
            'inference_time_ms': inference_time,
            'total_response_time_ms': total_time
        }
        
        await detection_system.save_performance_metrics(metrics)
        
        # 通知処理
        if should_alert:
            logger.info(f"[ALERT] Device: {device_id}, Person count: {person_count}")
            # LINE通知を送信（テスト用に一時無効化）
            # try:
            #     line_notifier.send_detection_alert(
            #         device_id=device_id,
            #         person_count=person_count,
            #         timestamp=timestamp,
            #         confidence_scores=person_detections
            #     )
            # except Exception as e:
            #     logger.error(f"Failed to send LINE notification: {e}")
        
        logger.info(f"Processed image from {device_id}: {person_count} persons detected")
        
        return {
            "event_id": event_id,
            "device_id": device_id,
            "timestamp": timestamp.isoformat(),
            "person_count": person_count,
            "anomaly_detected": should_alert,
            "confidence_scores": person_detections,
            "processing_time_ms": total_time
        }
    
    except Exception as e:
        logger.error(f"Error processing image from {device_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@app.get("/events")
async def get_events(device_id: Optional[str] = None, limit: int = 100):
    """イベント履歴を取得"""
    events = []
    
    if detection_system.events_csv.exists():
        with open(detection_system.events_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if device_id is None or row['device_id'] == device_id:
                    events.append(row)
                if len(events) >= limit:
                    break
    
    return {"events": events[::-1]}  # 最新順

@app.get("/metrics")
async def get_metrics(device_id: Optional[str] = None, limit: int = 100):
    """パフォーマンスメトリクスを取得"""
    metrics = []
    
    if detection_system.performance_csv.exists():
        with open(detection_system.performance_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if device_id is None or row['device_id'] == device_id:
                    metrics.append(row)
                if len(metrics) >= limit:
                    break
    
    return {"metrics": metrics[::-1]}  # 最新順

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=os.getenv('SERVER_HOST', '0.0.0.0'),
        port=int(os.getenv('SERVER_PORT', 8000)),
        reload=True
    )
