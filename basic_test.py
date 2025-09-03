#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
シンプルなサーバテストスクリプト
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """必要なモジュールのインポートテスト"""
    print("📦 モジュールインポートテスト...")
    
    try:
        import fastapi
        print(f"✅ FastAPI: {fastapi.__version__}")
    except ImportError as e:
        print(f"❌ FastAPI インポートエラー: {e}")
        return False
    
    try:
        import uvicorn
        print(f"✅ Uvicorn: {uvicorn.__version__}")
    except ImportError as e:
        print(f"❌ Uvicorn インポートエラー: {e}")
        return False
    
    try:
        import cv2
        print(f"✅ OpenCV: {cv2.__version__}")
    except ImportError as e:
        print(f"❌ OpenCV インポートエラー: {e}")
        return False
    
    try:
        import ultralytics
        print(f"✅ Ultralytics: {ultralytics.__version__}")
    except ImportError as e:
        print(f"❌ Ultralytics インポートエラー: {e}")
        return False
    
    try:
        import torch
        print(f"✅ PyTorch: {torch.__version__}")
    except ImportError as e:
        print(f"❌ PyTorch インポートエラー: {e}")
        return False
    
    return True

def test_yolo_model():
    """YOLOモデルの読み込みテスト"""
    print("\n🤖 YOLOモデルテスト...")
    
    try:
        from ultralytics import YOLO
        model = YOLO('yolov8n.pt')  # 初回実行時はダウンロードされる
        print("✅ YOLOv8nモデル読み込み成功")
        
        # テスト画像で推論
        import numpy as np
        test_image = np.zeros((640, 640, 3), dtype=np.uint8)
        results = model(test_image, verbose=False)
        print("✅ モデル推論テスト成功")
        
        return True
    except Exception as e:
        print(f"❌ YOLOモデルテストエラー: {e}")
        return False

def test_opencv():
    """OpenCVテスト"""
    print("\n📷 OpenCVテスト...")
    
    try:
        import cv2
        import numpy as np
        
        # テスト画像を作成
        test_image = np.zeros((360, 640, 3), dtype=np.uint8)
        cv2.putText(test_image, "TEST", (250, 180), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
        
        # JPEG圧縮テスト
        _, encoded = cv2.imencode('.jpg', test_image, [cv2.IMWRITE_JPEG_QUALITY, 80])
        print(f"✅ JPEG圧縮テスト成功 (サイズ: {len(encoded)} bytes)")
        
        return True
    except Exception as e:
        print(f"❌ OpenCVテストエラー: {e}")
        return False

def test_fastapi_basic():
    """FastAPIの基本テスト"""
    print("\n🚀 FastAPI基本テスト...")
    
    try:
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        
        # シンプルなFastAPIアプリ
        app = FastAPI()
        
        @app.get("/")
        def read_root():
            return {"status": "ok", "message": "FastAPI working"}
        
        # テストクライアント
        with TestClient(app) as client:
            response = client.get("/")
        
        if response.status_code == 200:
            print("✅ FastAPI基本テスト成功")
            return True
        else:
            print(f"❌ FastAPI テストエラー: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ FastAPIテストエラー: {e}")
        return False

def main():
    print("🧪 Edge Anomaly Detection System - 基本テスト\n")
    
    tests = [
        ("モジュールインポート", test_imports),
        ("OpenCV", test_opencv),
        ("FastAPI基本", test_fastapi_basic),
        ("YOLOモデル", test_yolo_model),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name}テスト失敗")
        except Exception as e:
            print(f"❌ {test_name}テスト例外エラー: {e}")
    
    print(f"\n📊 テスト結果: {passed}/{total} 通過")
    
    if passed == total:
        print("🎉 すべてのテストが成功しました！")
        print("次は 'python server/main.py' でサーバを起動できます。")
        return True
    else:
        print("⚠️  一部のテストが失敗しました。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
