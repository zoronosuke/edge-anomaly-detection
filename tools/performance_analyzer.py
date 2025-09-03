import csv
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime, timedelta
import argparse
import numpy as np

class PerformanceAnalyzer:
    def __init__(self, data_dir: str = "./data"):
        self.data_dir = Path(data_dir)
        self.events_csv = self.data_dir / "events.csv"
        self.performance_csv = self.data_dir / "performance_metrics.csv"
    
    def load_events(self) -> pd.DataFrame:
        """イベントデータを読み込み"""
        if not self.events_csv.exists():
            return pd.DataFrame()
        
        df = pd.read_csv(self.events_csv)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    
    def load_performance_metrics(self) -> pd.DataFrame:
        """パフォーマンスメトリクスを読み込み"""
        if not self.performance_csv.exists():
            return pd.DataFrame()
        
        df = pd.read_csv(self.performance_csv)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    
    def analyze_detection_performance(self) -> dict:
        """検出性能を分析"""
        events_df = self.load_events()
        
        if events_df.empty:
            return {"error": "No event data found"}
        
        total_events = len(events_df)
        anomaly_events = len(events_df[events_df['anomaly_flag'] == True])
        
        # デバイス別統計
        device_stats = events_df.groupby('device_id').agg({
            'person_count': ['count', 'sum', 'mean'],
            'anomaly_flag': 'sum',
            'processing_time_ms': 'mean'
        }).round(2)
        
        # 時間別統計
        events_df['hour'] = events_df['timestamp'].dt.hour
        hourly_stats = events_df.groupby('hour').agg({
            'person_count': 'sum',
            'anomaly_flag': 'sum'
        })
        
        return {
            "total_events": total_events,
            "anomaly_events": anomaly_events,
            "anomaly_rate": anomaly_events / total_events if total_events > 0 else 0,
            "device_statistics": device_stats.to_dict(),
            "hourly_statistics": hourly_stats.to_dict()
        }
    
    def analyze_communication_performance(self) -> dict:
        """通信性能を分析"""
        perf_df = self.load_performance_metrics()
        
        if perf_df.empty:
            return {"error": "No performance data found"}
        
        # 全体統計
        overall_stats = {
            "total_requests": len(perf_df),
            "avg_response_time_ms": perf_df['total_response_time_ms'].mean(),
            "avg_inference_time_ms": perf_df['inference_time_ms'].mean(),
            "avg_request_size_kb": perf_df['request_size_bytes'].mean() / 1024,
            "p95_response_time_ms": perf_df['total_response_time_ms'].quantile(0.95),
            "p99_response_time_ms": perf_df['total_response_time_ms'].quantile(0.99)
        }
        
        # デバイス別統計
        device_perf = perf_df.groupby('device_id').agg({
            'total_response_time_ms': ['mean', 'std', 'min', 'max'],
            'inference_time_ms': ['mean', 'std'],
            'request_size_bytes': ['mean', 'std']
        }).round(2)
        
        return {
            "overall_statistics": overall_stats,
            "device_performance": device_perf.to_dict()
        }
    
    def generate_report(self, output_file: str = None):
        """分析レポートを生成"""
        detection_analysis = self.analyze_detection_performance()
        communication_analysis = self.analyze_communication_performance()
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "detection_performance": detection_analysis,
            "communication_performance": communication_analysis
        }
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print(f"Report saved to {output_file}")
        
        return report
    
    def plot_performance_charts(self, output_dir: str = "./charts"):
        """パフォーマンスチャートを生成"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # データ読み込み
        events_df = self.load_events()
        perf_df = self.load_performance_metrics()
        
        if events_df.empty and perf_df.empty:
            print("No data available for plotting")
            return
        
        # スタイル設定
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # 1. 検出数の時系列グラフ
        if not events_df.empty:
            plt.figure(figsize=(12, 6))
            events_df.set_index('timestamp')['person_count'].resample('H').sum().plot()
            plt.title('Person Detection Count Over Time')
            plt.xlabel('Time')
            plt.ylabel('Total Person Count')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(output_path / 'detection_timeline.png', dpi=300, bbox_inches='tight')
            plt.close()
        
        # 2. レスポンス時間の分布
        if not perf_df.empty:
            plt.figure(figsize=(10, 6))
            plt.hist(perf_df['total_response_time_ms'], bins=50, alpha=0.7, edgecolor='black')
            plt.title('Response Time Distribution')
            plt.xlabel('Response Time (ms)')
            plt.ylabel('Frequency')
            plt.axvline(perf_df['total_response_time_ms'].mean(), color='red', linestyle='--', label='Mean')
            plt.axvline(perf_df['total_response_time_ms'].quantile(0.95), color='orange', linestyle='--', label='95th percentile')
            plt.legend()
            plt.tight_layout()
            plt.savefig(output_path / 'response_time_distribution.png', dpi=300, bbox_inches='tight')
            plt.close()
        
        # 3. デバイス別パフォーマンス比較
        if not perf_df.empty and 'device_id' in perf_df.columns:
            plt.figure(figsize=(12, 8))
            device_groups = perf_df.groupby('device_id')['total_response_time_ms']
            device_groups.boxplot()
            plt.title('Response Time by Device')
            plt.xlabel('Device ID')
            plt.ylabel('Response Time (ms)')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(output_path / 'device_performance_comparison.png', dpi=300, bbox_inches='tight')
            plt.close()
        
        # 4. 推論時間 vs 総処理時間
        if not perf_df.empty:
            plt.figure(figsize=(10, 6))
            plt.scatter(perf_df['inference_time_ms'], perf_df['total_response_time_ms'], alpha=0.6)
            plt.title('Inference Time vs Total Response Time')
            plt.xlabel('Inference Time (ms)')
            plt.ylabel('Total Response Time (ms)')
            plt.tight_layout()
            plt.savefig(output_path / 'inference_vs_total_time.png', dpi=300, bbox_inches='tight')
            plt.close()
        
        print(f"Charts saved to {output_path}")
    
    def export_summary_csv(self, output_file: str = "performance_summary.csv"):
        """サマリーをCSVで出力"""
        events_df = self.load_events()
        perf_df = self.load_performance_metrics()
        
        summary_data = []
        
        if not events_df.empty:
            for device in events_df['device_id'].unique():
                device_events = events_df[events_df['device_id'] == device]
                device_perf = perf_df[perf_df['device_id'] == device] if not perf_df.empty else pd.DataFrame()
                
                summary = {
                    'device_id': device,
                    'total_events': len(device_events),
                    'total_detections': device_events['person_count'].sum(),
                    'anomaly_events': device_events['anomaly_flag'].sum(),
                    'avg_persons_per_event': device_events['person_count'].mean(),
                    'avg_processing_time_ms': device_events['processing_time_ms'].mean() if 'processing_time_ms' in device_events.columns else None,
                    'avg_response_time_ms': device_perf['total_response_time_ms'].mean() if not device_perf.empty else None,
                    'p95_response_time_ms': device_perf['total_response_time_ms'].quantile(0.95) if not device_perf.empty else None,
                    'avg_request_size_kb': device_perf['request_size_bytes'].mean() / 1024 if not device_perf.empty else None
                }
                summary_data.append(summary)
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"Summary exported to {output_file}")
        
        return summary_df

def main():
    parser = argparse.ArgumentParser(description='Performance Analysis Tool')
    parser.add_argument('--data-dir', default='./data', help='Data directory path')
    parser.add_argument('--output-report', help='Output JSON report file')
    parser.add_argument('--output-csv', help='Output CSV summary file')
    parser.add_argument('--charts-dir', default='./charts', help='Charts output directory')
    parser.add_argument('--no-charts', action='store_true', help='Skip chart generation')
    
    args = parser.parse_args()
    
    analyzer = PerformanceAnalyzer(args.data_dir)
    
    # レポート生成
    report = analyzer.generate_report(args.output_report)
    
    # CSVサマリー出力
    if args.output_csv:
        analyzer.export_summary_csv(args.output_csv)
    
    # チャート生成
    if not args.no_charts:
        try:
            analyzer.plot_performance_charts(args.charts_dir)
        except ImportError:
            print("matplotlib/seaborn not available, skipping chart generation")
        except Exception as e:
            print(f"Error generating charts: {e}")
    
    # コンソール出力
    print("\n=== Detection Performance ===")
    if 'error' not in report['detection_performance']:
        dp = report['detection_performance']
        print(f"Total events: {dp['total_events']}")
        print(f"Anomaly events: {dp['anomaly_events']}")
        print(f"Anomaly rate: {dp['anomaly_rate']:.2%}")
    
    print("\n=== Communication Performance ===")
    if 'error' not in report['communication_performance']:
        cp = report['communication_performance']['overall_statistics']
        print(f"Total requests: {cp['total_requests']}")
        print(f"Avg response time: {cp['avg_response_time_ms']:.1f}ms")
        print(f"Avg inference time: {cp['avg_inference_time_ms']:.1f}ms")
        print(f"95th percentile response time: {cp['p95_response_time_ms']:.1f}ms")

if __name__ == "__main__":
    main()
