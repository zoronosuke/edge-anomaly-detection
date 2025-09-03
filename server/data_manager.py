"""
データ管理システム（CSV/JSON ベース）
"""

import os
import csv
import json
import threading
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path
import pandas as pd

from models import EventRecord, SystemLog


class DataManager:
    """CSV/JSON ファイルベースのデータ管理システム"""
    
    def __init__(self):
        self.data_dir = Path(os.getenv("DATA_DIR", "./data"))
        self.events_csv_path = Path(os.getenv("EVENTS_CSV", "./data/events.csv"))
        self.logs_json_path = Path(os.getenv("SYSTEM_LOGS_JSON", "./data/system_logs.json"))
        
        # スレッドセーフ用のロック
        self._csv_lock = threading.Lock()
        self._json_lock = threading.Lock()
        
        # ディレクトリ作成
        self.data_dir.mkdir(exist_ok=True)
        
        # CSVファイルの初期化
        self._init_csv_file()
        
        # JSONファイルの初期化
        self._init_json_file()
    
    def _init_csv_file(self):
        """CSVファイルの初期化（ヘッダー作成）"""
        if not self.events_csv_path.exists():
            with open(self.events_csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=[
                    "event_id", "device_id", "timestamp", "person_count",
                    "anomaly_flag", "image_filename", "confidence_threshold", 
                    "processing_time_ms"
                ])
                writer.writeheader()
    
    def _init_json_file(self):
        """JSONファイルの初期化"""
        if not self.logs_json_path.exists():
            with open(self.logs_json_path, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    def save_event(self, event: EventRecord) -> bool:
        """イベントをCSVファイルに保存"""
        try:
            with self._csv_lock:
                with open(self.events_csv_path, "a", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=[
                        "event_id", "device_id", "timestamp", "person_count",
                        "anomaly_flag", "image_filename", "confidence_threshold",
                        "processing_time_ms"
                    ])
                    writer.writerow(event.to_csv_row())
            return True
        except Exception as e:
            print(f"❌ CSVイベント保存エラー: {e}")
            return False
    
    def save_system_log(self, log: SystemLog) -> bool:
        """システムログをJSONファイルに保存"""
        try:
            with self._json_lock:
                # 既存ログの読み込み
                logs = []
                if self.logs_json_path.exists():
                    with open(self.logs_json_path, "r", encoding="utf-8") as f:
                        logs = json.load(f)
                
                # 新しいログを追加
                logs.append(log.to_dict())
                
                # ログサイズ制限（最新1000件まで）
                if len(logs) > 1000:
                    logs = logs[-1000:]
                
                # ファイルに保存
                with open(self.logs_json_path, "w", encoding="utf-8") as f:
                    json.dump(logs, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"❌ JSONログ保存エラー: {e}")
            return False
    
    def get_events(
        self, 
        device_id: Optional[str] = None,
        limit: int = 50,
        anomaly_only: bool = False
    ) -> List[Dict[str, Any]]:
        """イベント一覧を取得"""
        try:
            if not self.events_csv_path.exists():
                return []
            
            # pandas で CSV を読み込み
            df = pd.read_csv(self.events_csv_path)
            
            # フィルタリング
            if device_id:
                df = df[df["device_id"] == device_id]
            
            if anomaly_only:
                df = df[df["anomaly_flag"] == True]
            
            # 最新順にソート
            df = df.sort_values("timestamp", ascending=False)
            
            # 制限適用
            df = df.head(limit)
            
            # 辞書形式で返す
            return df.to_dict("records")
            
        except Exception as e:
            print(f"❌ イベント取得エラー: {e}")
            return []
    
    def get_recent_events(self, device_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """特定デバイスの最新イベントを取得"""
        return self.get_events(device_id=device_id, limit=limit)
    
    def get_system_logs(
        self,
        device_id: Optional[str] = None,
        level: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """システムログを取得"""
        try:
            if not self.logs_json_path.exists():
                return []
            
            with open(self.logs_json_path, "r", encoding="utf-8") as f:
                logs = json.load(f)
            
            # フィルタリング
            filtered_logs = []
            for log in logs:
                if device_id and log.get("device_id") != device_id:
                    continue
                if level and log.get("level") != level:
                    continue
                filtered_logs.append(log)
            
            # 最新順にソート
            filtered_logs.sort(key=lambda x: x["timestamp"], reverse=True)
            
            # 制限適用
            return filtered_logs[:limit]
            
        except Exception as e:
            print(f"❌ ログ取得エラー: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """統計情報を取得"""
        try:
            stats = {
                "total_events": 0,
                "total_anomalies": 0,
                "device_counts": {},
                "recent_activity": {}
            }
            
            if self.events_csv_path.exists():
                df = pd.read_csv(self.events_csv_path)
                
                stats["total_events"] = len(df)
                stats["total_anomalies"] = len(df[df["anomaly_flag"] == True])
                
                # デバイス別統計
                device_stats = df.groupby("device_id").agg({
                    "event_id": "count",
                    "anomaly_flag": "sum"
                }).to_dict("index")
                
                for device_id, data in device_stats.items():
                    stats["device_counts"][device_id] = {
                        "total_events": data["event_id"],
                        "anomalies": data["anomaly_flag"]
                    }
                
                # 過去24時間の活動
                df["timestamp"] = pd.to_datetime(df["timestamp"])
                recent_df = df[df["timestamp"] > (pd.Timestamp.now() - pd.Timedelta(days=1))]
                stats["recent_activity"] = {
                    "events_24h": len(recent_df),
                    "anomalies_24h": len(recent_df[recent_df["anomaly_flag"] == True])
                }
            
            return stats
            
        except Exception as e:
            print(f"❌ 統計取得エラー: {e}")
            return {}
