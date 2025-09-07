#!/usr/bin/env python3
"""
Jetson Nano環境確認スクリプト
JetPack 4.6.6 + Python 3.12の互換性問題をチェック
"""

import sys
import os
import platform
import subprocess
from pathlib import Path

def check_python_version():
    """Pythonバージョンの確認"""
    version = sys.version_info
    print(f"Python Version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor == 8:
        return "compatible", "✓ JetPack 4.6.6と互換性あり"
    elif version.major == 3 and version.minor == 12:
        return "incompatible", "⚠ JetPack 4.6.6との互換性問題あり - Python 3.8推奨"
    else:
        return "unknown", f"? Python {version.major}.{version.minor}の互換性は不明"

def check_jetpack_info():
    """JetPackバージョンの確認"""
    try:
        with open('/etc/nv_tegra_release', 'r') as f:
            tegra_info = f.read().strip()
        print(f"Tegra Release: {tegra_info}")
        
        if "R32.7" in tegra_info:
            return "jetpack_4_6", "JetPack 4.6.x系統検出"
        else:
            return "unknown", f"JetPackバージョン不明: {tegra_info}"
    except FileNotFoundError:
        return "not_jetson", "Jetson Nanoではありません"

def check_critical_packages():
    """重要パッケージの確認"""
    packages = {
        'ultralytics': 'YOLO v8',
        'torch': 'PyTorch',
        'torchvision': 'TorchVision', 
        'cv2': 'OpenCV',
        'fastapi': 'FastAPI',
        'uvicorn': 'Uvicorn',
        'aiofiles': 'Async File I/O'
    }
    
    results = {}
    for pkg, description in packages.items():
        try:
            if pkg == 'cv2':
                import cv2
                version = cv2.__version__
            else:
                module = __import__(pkg)
                version = getattr(module, '__version__', 'unknown')
            
            results[pkg] = {'status': 'ok', 'version': version, 'description': description}
        except ImportError:
            results[pkg] = {'status': 'missing', 'version': None, 'description': description}
    
    return results

def check_gpu_support():
    """GPU/CUDAサポートの確認"""
    gpu_info = {}
    
    # CUDA確認
    try:
        result = subprocess.run(['nvcc', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            gpu_info['cuda'] = 'available'
        else:
            gpu_info['cuda'] = 'not_available'
    except FileNotFoundError:
        gpu_info['cuda'] = 'not_installed'
    
    # PyTorch CUDA確認
    try:
        import torch
        gpu_info['pytorch_cuda'] = torch.cuda.is_available()
        if torch.cuda.is_available():
            gpu_info['gpu_name'] = torch.cuda.get_device_name(0)
    except ImportError:
        gpu_info['pytorch_cuda'] = 'pytorch_not_installed'
    
    return gpu_info

def generate_recommendations(python_status, jetpack_status, package_results, gpu_info):
    """推奨対応策の生成"""
    recommendations = []
    
    if python_status == "incompatible" and jetpack_status == "jetpack_4_6":
        recommendations.extend([
            "🚨 CRITICAL: Python 3.12はJetPack 4.6.6と互換性がありません",
            "",
            "推奨対応策:",
            "1. Docker環境の利用 (最推奨)",
            "   sudo docker run --runtime nvidia -it --rm \\",
            "     --network host --ipc=host \\",
            "     -v $(pwd):/workspace \\",
            "     nvcr.io/nvidia/l4t-ml:r32.7.1-py3",
            "",
            "2. Python 3.8の併設インストール",
            "   sudo apt install python3.8 python3.8-venv python3.8-dev",
            "   python3.8 -m venv ~/venv-jetson-py38",
            "   source ~/venv-jetson-py38/bin/activate",
            ""
        ])
    
    # パッケージ不足の確認
    missing_packages = [pkg for pkg, info in package_results.items() if info['status'] == 'missing']
    if missing_packages:
        recommendations.extend([
            f"📦 不足パッケージ: {', '.join(missing_packages)}",
            "インストールコマンド:",
            f"   pip install {' '.join(missing_packages)}",
            ""
        ])
    
    # GPU関連の推奨事項
    if gpu_info.get('pytorch_cuda') == False:
        recommendations.extend([
            "⚠ PyTorchでCUDAが利用できません",
            "Jetson Nano向けPyTorchの再インストールが必要です",
            ""
        ])
    
    return recommendations

def main():
    print("=" * 60)
    print("Jetson Nano環境互換性チェック")
    print("=" * 60)
    
    # システム情報
    print(f"Platform: {platform.platform()}")
    print(f"Architecture: {platform.machine()}")
    print(f"Python Executable: {sys.executable}")
    print()
    
    # Pythonバージョンチェック
    print("1. Python Version Check")
    python_status, python_msg = check_python_version()
    print(f"   {python_msg}")
    print()
    
    # JetPackチェック  
    print("2. JetPack Version Check")
    jetpack_status, jetpack_msg = check_jetpack_info()
    print(f"   {jetpack_msg}")
    print()
    
    # パッケージチェック
    print("3. Critical Package Check")
    package_results = check_critical_packages()
    for pkg, info in package_results.items():
        status_icon = "✓" if info['status'] == 'ok' else "✗"
        version_info = f" (v{info['version']})" if info['version'] else ""
        print(f"   {status_icon} {info['description']}: {info['status']}{version_info}")
    print()
    
    # GPU/CUDAチェック
    print("4. GPU/CUDA Support Check")
    gpu_info = check_gpu_support()
    for key, value in gpu_info.items():
        print(f"   {key}: {value}")
    print()
    
    # 推奨事項
    print("5. Recommendations")
    recommendations = generate_recommendations(python_status, jetpack_status, package_results, gpu_info)
    for rec in recommendations:
        print(f"   {rec}")
    
    print("=" * 60)
    print("チェック完了")
    print("=" * 60)

if __name__ == "__main__":
    main()
