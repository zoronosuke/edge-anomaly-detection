"""
システム管理・監視用のツール
"""

import argparse
import json
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta
try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


def analyze_events(csv_path: str):
    """イベントデータの分析"""
    try:
        df = pd.read_csv(csv_path)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        print("="*60)
        print("📊 イベント分析レポート")
        print("="*60)
        
        # 基本統計
        total_events = len(df)
        total_anomalies = len(df[df['anomaly_flag'] == True])
        anomaly_rate = (total_anomalies / total_events * 100) if total_events > 0 else 0
        
        print(f"📈 総イベント数: {total_events}")
        print(f"🚨 異常検出数: {total_anomalies}")
        print(f"📊 異常率: {anomaly_rate:.2f}%")
        print()
        
        # デバイス別統計
        print("🖥️ デバイス別統計:")
        device_stats = df.groupby('device_id').agg({
            'event_id': 'count',
            'anomaly_flag': 'sum',
            'person_count': 'mean'
        }).round(2)
        device_stats.columns = ['総イベント', '異常数', '平均人数']
        print(device_stats)
        print()
        
        # 時間別分析
        df['hour'] = df['timestamp'].dt.hour
        hourly_stats = df.groupby('hour').agg({
            'event_id': 'count',
            'anomaly_flag': 'sum'
        })
        
        print("⏰ 時間別統計 (上位5時間):")
        top_hours = hourly_stats.sort_values('anomaly_flag', ascending=False).head()
        print(top_hours)
        print()
        
        # 最近の活動
        recent_threshold = datetime.now() - timedelta(hours=24)
        recent_df = df[df['timestamp'] > recent_threshold]
        
        print(f"🕐 過去24時間の活動:")
        print(f"   イベント数: {len(recent_df)}")
        print(f"   異常数: {len(recent_df[recent_df['anomaly_flag'] == True])}")
        
        if len(recent_df) > 0:
            latest_event = recent_df.sort_values('timestamp').iloc[-1]
            print(f"   最新イベント: {latest_event['timestamp']} "
                  f"({latest_event['device_id']})")
        
    except FileNotFoundError:
        print(f"❌ ファイルが見つかりません: {csv_path}")
    except Exception as e:
        print(f"❌ 分析エラー: {e}")


def analyze_logs(json_path: str):
    """システムログの分析"""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            logs = json.load(f)
        
        if not logs:
            print("📝 ログデータがありません")
            return
        
        print("="*60)
        print("📝 システムログ分析")
        print("="*60)
        
        # ログレベル別統計
        levels = {}
        for log in logs:
            level = log.get('level', 'UNKNOWN')
            levels[level] = levels.get(level, 0) + 1
        
        print("📊 ログレベル別統計:")
        for level, count in sorted(levels.items()):
            print(f"   {level}: {count}")
        print()
        
        # エラーログの詳細
        error_logs = [log for log in logs if log.get('level') == 'ERROR']
        if error_logs:
            print(f"❌ エラーログ (最新5件):")
            for log in error_logs[-5:]:
                timestamp = log.get('timestamp', 'N/A')
                message = log.get('message', 'N/A')
                device_id = log.get('device_id', 'N/A')
                print(f"   {timestamp} [{device_id}] {message}")
        else:
            print("✅ エラーログはありません")
        
    except FileNotFoundError:
        print(f"❌ ファイルが見つかりません: {json_path}")
    except Exception as e:
        print(f"❌ ログ分析エラー: {e}")


def cleanup_old_data(data_dir: str, days: int = 30):
    """古いデータのクリーンアップ"""
    data_path = Path(data_dir)
    cutoff_date = datetime.now() - timedelta(days=days)
    
    print(f"🧹 データクリーンアップ ({days}日前より古いデータを削除)")
    
    # 古い画像ファイルの削除
    images_dir = data_path / "images"
    if images_dir.exists():
        deleted_count = 0
        for image_file in images_dir.glob("*.jpg"):
            if image_file.stat().st_mtime < cutoff_date.timestamp():
                image_file.unlink()
                deleted_count += 1
        
        print(f"   削除した画像ファイル: {deleted_count}")
    
    # CSV のバックアップと最適化
    events_csv = data_path / "events.csv"
    if events_csv.exists():
        try:
            df = pd.read_csv(events_csv)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # 古いレコードを除外
            df_filtered = df[df['timestamp'] > cutoff_date]
            removed_count = len(df) - len(df_filtered)
            
            if removed_count > 0:
                # バックアップ作成
                backup_path = events_csv.with_suffix('.backup.csv')
                df.to_csv(backup_path, index=False)
                
                # フィルター済みデータで更新
                df_filtered.to_csv(events_csv, index=False)
                
                print(f"   削除したイベントレコード: {removed_count}")
                print(f"   バックアップ: {backup_path}")
            else:
                print("   削除対象のイベントレコードはありません")
                
        except Exception as e:
            print(f"   ❌ CSVクリーンアップエラー: {e}")


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description="System Management Tools")
    parser.add_argument("command", choices=["analyze", "logs", "cleanup"],
                       help="実行するコマンド")
    parser.add_argument("--data-dir", default="./data",
                       help="データディレクトリ (default: ./data)")
    parser.add_argument("--days", type=int, default=30,
                       help="クリーンアップ対象日数 (default: 30)")
    
    args = parser.parse_args()
    
    data_dir = Path(args.data_dir)
    
    if args.command == "analyze":
        events_csv = data_dir / "events.csv"
        analyze_events(str(events_csv))
    
    elif args.command == "logs":
        logs_json = data_dir / "system_logs.json"
        analyze_logs(str(logs_json))
    
    elif args.command == "cleanup":
        cleanup_old_data(str(data_dir), args.days)


if __name__ == "__main__":
    main()
