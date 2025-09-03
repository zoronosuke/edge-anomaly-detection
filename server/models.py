"""
データモデル定義
"""

from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass

@dataclass
class EventRecord:
    """検出イベントのレコード"""
    event_id: str
    device_id: str
    timestamp: datetime
    person_count: int
    anomaly_flag: bool
    image_filename: Optional[str] = None
    confidence_threshold: float = 0.5
    processing_time_ms: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            "event_id": self.event_id,
            "device_id": self.device_id,
            "timestamp": self.timestamp.isoformat(),
            "person_count": self.person_count,
            "anomaly_flag": self.anomaly_flag,
            "image_filename": self.image_filename,
            "confidence_threshold": self.confidence_threshold,
            "processing_time_ms": self.processing_time_ms
        }
    
    def to_csv_row(self) -> Dict[str, Any]:
        """CSV用の行データに変換"""
        return {
            "event_id": self.event_id,
            "device_id": self.device_id,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S.%f"),
            "person_count": self.person_count,
            "anomaly_flag": self.anomaly_flag,
            "image_filename": self.image_filename or "",
            "confidence_threshold": self.confidence_threshold,
            "processing_time_ms": self.processing_time_ms or 0
        }

@dataclass
class SystemLog:
    """システムログのレコード"""
    log_id: str
    timestamp: datetime
    level: str  # INFO, WARNING, ERROR
    device_id: Optional[str] = None
    message: str = ""
    details: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            "log_id": self.log_id,
            "timestamp": self.timestamp.isoformat(),
            "level": self.level,
            "device_id": self.device_id,
            "message": self.message,
            "details": self.details or {}
        }
