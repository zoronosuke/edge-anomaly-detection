"""
エッジ異常検知システム - メインサーバー
研究用システムでCSV/JSONファイルベースのデータ保存を使用
"""

import os
import io
import csv
import json
import time
import uuid
from datetime import datetime
from typing import Dict, Optional, List
from pathlib import Path

import uvicorn
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Header, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import cv2
import numpy as np
from PIL import Image
from ultralytics import YOLO
from dotenv import load_dotenv
import pandas as pd

from models import EventRecord, SystemLog
from line_notifier import LineNotifier
from data_manager import DataManager

# 環境変数の読み込み
load_dotenv()

app = FastAPI(
    title="Edge Anomaly Detection System",
    description="エッジデバイス用異常検知システム（研究用）",
    version="1.0.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# グローバル変数
yolo_model: Optional[YOLO] = None
line_notifier: Optional[LineNotifier] = None
data_manager: DataManager = None

# デバイスごとの状態管理
device_states: Dict[str, Dict] = {}

def get_device_state(device_id: str) -> Dict:
    """デバイス状態を取得（存在しない場合は初期化）"""
    if device_id not in device_states:
        device_states[device_id] = {
            "last_alert_at": 0,
            "last_event_signature": "",
            "last_event_time": 0,
            "total_detections": 0
        }
    return device_states[device_id]

@app.on_event("startup")
async def startup_event():
    """アプリケーション起動時の初期化"""
    global yolo_model, line_notifier, data_manager
    
    print("🚀 Edge Anomaly Detection System を起動中...")
    
    # データディレクトリの作成
    data_dir = Path(os.getenv("DATA_DIR", "./data"))
    images_dir = Path(os.getenv("IMAGES_DIR", "./data/images"))
    data_dir.mkdir(exist_ok=True)
    images_dir.mkdir(exist_ok=True)
    
    # データマネージャーの初期化
    try:
        data_manager = DataManager()
        print("✅ データマネージャー初期化完了")
    except Exception as e:
        print(f"❌ データマネージャー初期化失敗: {e}")
    
    # YOLOモデルの読み込み
    try:
        model_path = os.getenv("YOLO_MODEL", "yolov8n.pt")
        print(f"📋 YOLOモデルを読み込み中: {model_path}")
        yolo_model = YOLO(model_path)
        print("✅ YOLOモデルの読み込み完了")
    except Exception as e:
        print(f"❌ YOLOモデルの読み込み失敗: {e}")
        yolo_model = None
    
    # LINE通知の初期化
    try:
        line_notifier = LineNotifier()
        print("✅ LINE通知システム初期化完了")
    except Exception as e:
        print(f"⚠️ LINE通知システム初期化失敗: {e}")
        line_notifier = None
    
    print("🎯 システム起動完了!")

@app.get("/")
async def root():
    """ヘルスチェック用エンドポイント"""
    return {
        "status": "running",
        "system": "Edge Anomaly Detection System",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "yolo_loaded": yolo_model is not None,
        "line_enabled": line_notifier is not None and line_notifier.is_enabled()
    }

@app.post("/ingest")
async def ingest_image(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    device_id: str = Form(...),
    ts: Optional[str] = Form(None),
    x_api_key: Optional[str] = Header(None)
):
    """
    エッジデバイスからの画像データ受信・処理エンドポイント
    """
    # API KEY検証
    expected_api_key = os.getenv("API_KEY")
    if expected_api_key and x_api_key != expected_api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    # タイムスタンプの処理
    if ts is None:
        timestamp = datetime.now()
    else:
        try:
            timestamp = datetime.fromisoformat(ts)
        except ValueError:
            timestamp = datetime.now()
    
    # ファイル形式チェック
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Image required.")
    
    try:
        # 画像の読み込み
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes))
        image_array = np.array(image)
        
        # 推論処理
        person_count = 0
        anomaly_detected = False
        
        if yolo_model is not None:
            try:
                results = yolo_model(image_array)
                
                # person クラス（クラスID=0）の検出
                for result in results:
                    boxes = result.boxes
                    if boxes is not None:
                        # confidence >= threshold の person を数える
                        conf_threshold = float(os.getenv("CONFIDENCE_THRESHOLD", "0.5"))
                        person_detections = boxes[
                            (boxes.cls == 0) & (boxes.conf >= conf_threshold)
                        ]
                        person_count = len(person_detections)
                        break
                
                # 異常判定（人が検出された場合）
                anomaly_detected = person_count > 0
                
            except Exception as e:
                print(f"⚠️ 推論エラー: {e}")
        
        # イベント記録
        event_id = str(uuid.uuid4())
        event_record = EventRecord(
            event_id=event_id,
            device_id=device_id,
            timestamp=timestamp,
            person_count=person_count,
            anomaly_flag=anomaly_detected,
            image_filename=f"{event_id}.jpg" if anomaly_detected else None,
            confidence_threshold=float(os.getenv("CONFIDENCE_THRESHOLD", "0.5"))
        )
        
        # バックグラウンドタスクで処理
        background_tasks.add_task(
            process_detection_result,
            event_record,
            image_bytes if anomaly_detected else None,
            device_id
        )
        
        return {
            "status": "success",
            "event_id": event_id,
            "device_id": device_id,
            "timestamp": timestamp.isoformat(),
            "person_count": person_count,
            "anomaly_detected": anomaly_detected,
            "processing_time_ms": int((datetime.now() - timestamp).total_seconds() * 1000)
        }
        
    except Exception as e:
        # エラーログ
        error_log = SystemLog(
            log_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            level="ERROR",
            device_id=device_id,
            message=f"画像処理エラー: {str(e)}",
            details={"error_type": type(e).__name__}
        )
        data_manager.save_system_log(error_log)
        
        raise HTTPException(status_code=500, detail=f"処理エラー: {str(e)}")

async def process_detection_result(
    event_record: EventRecord,
    image_bytes: Optional[bytes],
    device_id: str
):
    """検出結果の後処理（通知・保存）"""
    try:
        # イベントをCSVに保存
        data_manager.save_event(event_record)
        
        # 画像保存（異常検出時のみ）
        if image_bytes and event_record.image_filename:
            image_path = Path(os.getenv("IMAGES_DIR", "./data/images")) / event_record.image_filename
            with open(image_path, "wb") as f:
                f.write(image_bytes)
        
        # デバイス状態の更新
        device_state = get_device_state(device_id)
        device_state["total_detections"] += 1
        
        # 通知処理（異常検出 + クールダウン条件）
        if event_record.anomaly_flag and line_notifier and line_notifier.is_enabled():
            current_time = time.time()
            cooldown_seconds = int(os.getenv("ALERT_COOLDOWN_SECONDS", "300"))
            
            # クールダウンチェック
            if current_time - device_state["last_alert_at"] >= cooldown_seconds:
                # 重複抑制チェック
                event_signature = f"{device_id}_{event_record.person_count}_{int(current_time/10)*10}"
                
                if event_signature != device_state["last_event_signature"]:
                    # LINE通知送信
                    message = f"""🚨 [人検出アラート]
デバイス: {device_id}
検出数: {event_record.person_count}人
時刻: {event_record.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
イベントID: {event_record.event_id}"""
                    
                    success = await line_notifier.send_message(message)
                    
                    if success:
                        device_state["last_alert_at"] = current_time
                        device_state["last_event_signature"] = event_signature
                        
                        # 通知ログ
                        notification_log = SystemLog(
                            log_id=str(uuid.uuid4()),
                            timestamp=datetime.now(),
                            level="INFO",
                            device_id=device_id,
                            message="LINE通知送信成功",
                            details={
                                "event_id": event_record.event_id,
                                "person_count": event_record.person_count
                            }
                        )
                        data_manager.save_system_log(notification_log)
        
        # 処理完了ログ
        process_log = SystemLog(
            log_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            level="INFO",
            device_id=device_id,
            message="検出処理完了",
            details={
                "event_id": event_record.event_id,
                "person_count": event_record.person_count,
                "anomaly_detected": event_record.anomaly_flag
            }
        )
        data_manager.save_system_log(process_log)
        
    except Exception as e:
        error_log = SystemLog(
            log_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            level="ERROR",
            device_id=device_id,
            message=f"後処理エラー: {str(e)}",
            details={"error_type": type(e).__name__}
        )
        data_manager.save_system_log(error_log)
        print(f"❌ 後処理エラー: {e}")

@app.get("/status/{device_id}")
async def get_device_status(device_id: str):
    """デバイス状態の取得"""
    device_state = get_device_state(device_id)
    recent_events = data_manager.get_recent_events(device_id, limit=10)
    
    return {
        "device_id": device_id,
        "state": device_state,
        "recent_events": recent_events,
        "system_status": {
            "yolo_loaded": yolo_model is not None,
            "line_enabled": line_notifier is not None and line_notifier.is_enabled()
        }
    }

@app.get("/events")
async def get_events(
    device_id: Optional[str] = None,
    limit: int = 50,
    anomaly_only: bool = False
):
    """イベント一覧の取得"""
    events = data_manager.get_events(
        device_id=device_id,
        limit=limit,
        anomaly_only=anomaly_only
    )
    return {"events": events, "count": len(events)}

@app.get("/logs")
async def get_system_logs(
    device_id: Optional[str] = None,
    level: Optional[str] = None,
    limit: int = 100
):
    """システムログの取得"""
    logs = data_manager.get_system_logs(
        device_id=device_id,
        level=level,
        limit=limit
    )
    return {"logs": logs, "count": len(logs)}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=os.getenv("SERVER_HOST", "0.0.0.0"),
        port=int(os.getenv("SERVER_PORT", "8000")),
        reload=True
    )
