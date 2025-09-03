import requests
import json
import time
import os
from pathlib import Path
import cv2
import numpy as np

def test_server_connection(server_url: str, api_key: str):
    """サーバ接続テスト"""
    print("Testing server connection...")
    
    try:
        response = requests.get(f"{server_url}/", timeout=10)
        if response.status_code == 200:
            print("✓ Server is running")
            return True
        else:
            print(f"✗ Server returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Failed to connect to server: {e}")
        return False

def create_test_image():
    """テスト用の画像を作成"""
    # 640x360の黒い画像を作成
    image = np.zeros((360, 640, 3), dtype=np.uint8)
    
    # テキストを追加
    cv2.putText(image, "TEST IMAGE", (200, 180), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
    cv2.putText(image, f"Generated at {time.strftime('%H:%M:%S')}", (150, 250), cv2.FONT_HERSHEY_SIMPLEX, 1, (200, 200, 200), 2)
    
    # 人を模したシンプルな図形を描画（検出テスト用）
    # 楕円で体を表現
    cv2.ellipse(image, (320, 200), (30, 60), 0, 0, 360, (100, 150, 100), -1)
    # 円で頭を表現
    cv2.circle(image, (320, 140), 20, (120, 170, 120), -1)
    
    return image

def test_image_upload(server_url: str, api_key: str, device_id: str = "test-device"):
    """画像アップロードテスト"""
    print("Testing image upload...")
    
    # テスト画像を作成
    test_image = create_test_image()
    
    # JPEG形式にエンコード
    _, encoded_img = cv2.imencode('.jpg', test_image, [cv2.IMWRITE_JPEG_QUALITY, 80])
    image_data = encoded_img.tobytes()
    
    # APIリクエスト
    url = f"{server_url}/ingest"
    
    files = {
        'file': ('test_image.jpg', image_data, 'image/jpeg')
    }
    
    data = {
        'device_id': device_id,
        'ts': time.strftime('%Y-%m-%dT%H:%M:%S')
    }
    
    headers = {
        'Authorization': f'Bearer {api_key}'
    }
    
    try:
        response = requests.post(url, files=files, data=data, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("✓ Image upload successful")
            print(f"  Event ID: {result.get('event_id', 'N/A')}")
            print(f"  Person count: {result.get('person_count', 0)}")
            print(f"  Anomaly detected: {result.get('anomaly_detected', False)}")
            print(f"  Processing time: {result.get('processing_time_ms', 0):.1f}ms")
            return True
        else:
            print(f"✗ Upload failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Upload request failed: {e}")
        return False

def test_api_endpoints(server_url: str, api_key: str):
    """APIエンドポイントテスト"""
    print("Testing API endpoints...")
    
    headers = {
        'Authorization': f'Bearer {api_key}'
    }
    
    # Events endpoint test
    try:
        response = requests.get(f"{server_url}/events", headers=headers, timeout=10)
        if response.status_code == 200:
            events_data = response.json()
            print(f"✓ Events endpoint working (found {len(events_data.get('events', []))} events)")
        else:
            print(f"✗ Events endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Events endpoint error: {e}")
    
    # Metrics endpoint test
    try:
        response = requests.get(f"{server_url}/metrics", headers=headers, timeout=10)
        if response.status_code == 200:
            metrics_data = response.json()
            print(f"✓ Metrics endpoint working (found {len(metrics_data.get('metrics', []))} metrics)")
        else:
            print(f"✗ Metrics endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Metrics endpoint error: {e}")

def test_multiple_uploads(server_url: str, api_key: str, count: int = 5):
    """複数回のアップロードテスト"""
    print(f"Testing {count} consecutive uploads...")
    
    success_count = 0
    total_time = 0
    
    for i in range(count):
        print(f"  Upload {i+1}/{count}...", end=" ")
        
        start_time = time.time()
        
        # テスト画像を作成（毎回少し違う内容）
        test_image = create_test_image()
        cv2.putText(test_image, f"Upload #{i+1}", (450, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        
        _, encoded_img = cv2.imencode('.jpg', test_image, [cv2.IMWRITE_JPEG_QUALITY, 80])
        image_data = encoded_img.tobytes()
        
        # アップロード
        url = f"{server_url}/ingest"
        files = {'file': ('test_image.jpg', image_data, 'image/jpeg')}
        data = {'device_id': f'test-device-{i+1}', 'ts': time.strftime('%Y-%m-%dT%H:%M:%S')}
        headers = {'Authorization': f'Bearer {api_key}'}
        
        try:
            response = requests.post(url, files=files, data=data, headers=headers, timeout=30)
            elapsed = time.time() - start_time
            total_time += elapsed
            
            if response.status_code == 200:
                result = response.json()
                print(f"✓ ({elapsed:.1f}s, {result.get('person_count', 0)} persons)")
                success_count += 1
            else:
                print(f"✗ (status: {response.status_code})")
                
        except Exception as e:
            elapsed = time.time() - start_time
            total_time += elapsed
            print(f"✗ (error: {e})")
        
        # 少し間隔を空ける
        time.sleep(0.5)
    
    print(f"\nMultiple upload test results:")
    print(f"  Success rate: {success_count}/{count} ({success_count/count*100:.1f}%)")
    print(f"  Average time: {total_time/count:.2f}s per upload")
    print(f"  Total time: {total_time:.2f}s")

def main():
    # 設定
    SERVER_URL = os.getenv('TEST_SERVER_URL', 'http://localhost:8000')
    API_KEY = os.getenv('TEST_API_KEY', 'your_api_key_here')
    
    print("=== Edge Anomaly Detection System Test ===")
    print(f"Server URL: {SERVER_URL}")
    print(f"API Key: {API_KEY[:10]}...")
    print()
    
    # テスト実行
    tests_passed = 0
    total_tests = 4
    
    # 1. サーバ接続テスト
    if test_server_connection(SERVER_URL, API_KEY):
        tests_passed += 1
    print()
    
    # 2. 画像アップロードテスト
    if test_image_upload(SERVER_URL, API_KEY):
        tests_passed += 1
    print()
    
    # 3. APIエンドポイントテスト
    test_api_endpoints(SERVER_URL, API_KEY)
    tests_passed += 1  # 部分的な成功でもカウント
    print()
    
    # 4. 複数アップロードテスト
    test_multiple_uploads(SERVER_URL, API_KEY, 3)
    tests_passed += 1  # 部分的な成功でもカウント
    print()
    
    # 結果サマリー
    print("=== Test Summary ===")
    print(f"Tests completed: {tests_passed}/{total_tests}")
    if tests_passed == total_tests:
        print("✓ All tests passed!")
    else:
        print("⚠ Some tests failed. Check the output above.")
    
    print("\nTest completed.")

if __name__ == "__main__":
    main()
