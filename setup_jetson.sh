#!/bin/bash
# Jetson Nano環境セットアップスクリプト
# JetPack 4.6.6 + Python 3.8環境の構築

set -e

echo "=========================================="
echo "Jetson Nano 環境セットアップ開始"
echo "=========================================="

# 基本情報の確認
echo "現在のシステム情報:"
echo "  Platform: $(uname -a)"
echo "  Python: $(python3 --version)"
echo ""

# JetPackバージョンの確認
if [ -f /etc/nv_tegra_release ]; then
    echo "Tegra Info: $(cat /etc/nv_tegra_release)"
else
    echo "警告: Jetson Nanoが検出されません"
fi
echo ""

# 依存関係競合の確認
echo "⚠️  numpy依存関係競合の解決オプション"
echo "numpy 1.19.5 vs ultralytics>=8.0.200 の競合が検出される場合があります。"
echo ""
echo "セットアップ方法を選択してください:"
echo "1) Docker環境での実行 (最推奨・競合なし)"
echo "2) numpy更新版 - Python 3.8仮想環境 (numpy>=1.22.2)"
echo "3) 互換版 - 古いultralytics使用 (numpy==1.19.5対応)"
echo "4) 現在のPython環境での強制実行 (非推奨)"
echo ""

read -p "選択してください [1-4]: " choice

case $choice in
    1)
        echo "=========================================="
        echo "Docker環境のセットアップ"
        echo "=========================================="
        
        # Dockerが利用可能かチェック
        if ! command -v docker &> /dev/null; then
            echo "エラー: Dockerがインストールされていません"
            echo "以下のコマンドでDockerをインストールしてください:"
            echo "curl -fsSL https://get.docker.com -o get-docker.sh"
            echo "sudo sh get-docker.sh"
            exit 1
        fi
        
        # nvidia-dockerの確認
        if ! docker info | grep -q nvidia; then
            echo "警告: nvidia-dockerが設定されていない可能性があります"
        fi
        
        # Dockerコンテナを起動
        echo "L4T MLコンテナを起動します..."
        sudo docker run --runtime nvidia -it --rm \
            --network host --ipc=host \
            --name jetson-edge-detection \
            -v $(pwd):/workspace \
            -w /workspace \
            -p 8000:8000 \
            nvcr.io/nvidia/l4t-ml:r32.7.1-py3 \
            bash -c "
                echo 'Container started successfully'
                echo 'Python version:' && python3 --version
                echo 'Installing project dependencies...'
                pip install fastapi uvicorn aiofiles requests python-dotenv
                pip install ultralytics>=8.0.200
                echo 'Setup completed!'
                echo 'Run: python3 server/main.py to start the server'
                bash
            "
        ;;
        
    2)
        echo "=========================================="
        echo "Python 3.8仮想環境 (numpy更新版)"
        echo "=========================================="
        
        # Python 3.8のインストール確認
        if ! command -v python3.8 &> /dev/null; then
            echo "Python 3.8をインストールします..."
            sudo apt update
            sudo apt install -y python3.8 python3.8-venv python3.8-dev python3.8-distutils
            
            # インストール確認
            if ! command -v python3.8 &> /dev/null; then
                echo "エラー: Python 3.8のインストールに失敗しました"
                exit 1
            fi
        fi
        
        # 仮想環境の作成
        VENV_PATH="$HOME/venv-jetson-py38"
        echo "仮想環境を作成します: $VENV_PATH"
        
        # 既存の仮想環境がある場合は削除
        if [ -d "$VENV_PATH" ]; then
            echo "既存の仮想環境を削除します..."
            rm -rf "$VENV_PATH"
        fi
        
        # 仮想環境の作成
        python3.8 -m venv "$VENV_PATH"
        
        # 仮想環境のアクティベート確認
        if [ ! -f "$VENV_PATH/bin/activate" ]; then
            echo "エラー: 仮想環境の作成に失敗しました"
            exit 1
        fi
        
        # 仮想環境のアクティベート
        echo "仮想環境をアクティベートします..."
        source "$VENV_PATH/bin/activate"
        
        # Python確認
        echo "仮想環境のPython: $(python --version)"
        
        # pipのアップグレード
        echo "pipをアップグレードします..."
        python -m pip install --upgrade pip
        
        # 【重要】numpy競合解決のため、最初にnumpyの新しいバージョンをインストール
        echo "numpy (更新版) をインストールして競合を解決します..."
        python -m pip install "numpy>=1.22.2"
        
        # システムパッケージのインストール（OpenCV等）
        echo "システムパッケージをインストールします..."
        sudo apt install -y libopencv-dev
        
        # その他の基本的な依存関係をインストール
        echo "基本パッケージをインストールします..."
        python -m pip install fastapi uvicorn aiofiles requests python-dotenv pillow
        
        # OpenCV Pythonのインストール
        echo "OpenCV Pythonをインストールします..."
        python -m pip install opencv-python
        
        # PyTorch（Jetson用）のインストール - 条件付き
        if [ -f /etc/nv_tegra_release ]; then
            echo "Jetson用PyTorchをインストールします..."
            TORCH_WHL="torch-1.10.0-cp38-cp38-linux_aarch64.whl"
            
            if [ ! -f "$TORCH_WHL" ]; then
                echo "PyTorch wheelをダウンロードします..."
                wget https://nvidia.box.com/shared/static/fjtbno0vpo676a25cgvuqc1wty0fkkg6.whl -O "$TORCH_WHL"
            fi
            
            python -m pip install "$TORCH_WHL"
            
            # torchvision
            echo "torchvisionをインストールします..."
            sudo apt install -y libjpeg-dev zlib1g-dev libopenblas-dev
            
            if [ ! -d "torchvision" ]; then
                git clone --branch v0.11.1 https://github.com/pytorch/vision torchvision
            fi
            
            cd torchvision
            python setup.py install
            cd ..
            rm -rf torchvision
        else
            echo "非Jetson環境では一般的なPyTorchをインストールします..."
            python -m pip install torch torchvision
        fi
        
        # 【最後に】ultralyticsをインストール（numpy>=1.22.2が準備済みなので競合しない）
        echo "ultralytics をインストールします..."
        python -m pip install "ultralytics>=8.0.200"
        
        # 環境アクティベーションスクリプトの作成
        echo "環境アクティベーションスクリプトを作成します..."
        cat > activate_jetson_env.sh << 'EOF'
#!/bin/bash
# Jetson Nano環境のアクティベート
export JETSON_ENV=1
export CUDA_VISIBLE_DEVICES=0

# 仮想環境のパス
VENV_PATH="$HOME/venv-jetson-py38"

# 仮想環境が存在するかチェック
if [ ! -f "$VENV_PATH/bin/activate" ]; then
    echo "エラー: 仮想環境が見つかりません: $VENV_PATH"
    echo "setup_jetson.shを再実行してください"
    return 1
fi

# 仮想環境をアクティベート
source "$VENV_PATH/bin/activate"

echo "🤖 Python 3.8環境がアクティブになりました"
echo "Python: $(python --version)"
echo "pip: $(pip --version)"

# パッケージバージョン確認と競合チェック
numpy_version=$(python -c "import numpy; print(numpy.__version__)" 2>/dev/null || echo "not installed")
ultralytics_version=$(python -c "import ultralytics; print(ultralytics.__version__)" 2>/dev/null || echo "not installed")

echo "numpy: $numpy_version"
echo "ultralytics: $ultralytics_version"

# 競合チェック
if [[ "$numpy_version" == "1.19."* ]] && [[ "$ultralytics_version" == "8.0.2"* ]]; then
    echo "⚠️  依存関係の競合が検出されました。"
    echo "   ./setup_jetson.sh を再実行してください。"
elif [[ "$numpy_version" == "1.22."* || "$numpy_version" == "1.2"[3-9]* ]] && [[ "$ultralytics_version" == "8.0.2"* ]]; then
    echo "✅ 依存関係は正常です（更新版）。"
else
    echo "ℹ️  パッケージ状態を確認してください。"
fi

# PyTorchの確認
if python -c "import torch" 2>/dev/null; then
    echo "PyTorch: $(python -c 'import torch; print(torch.__version__)')"
    echo "CUDA Available: $(python -c 'import torch; print(torch.cuda.is_available())')"
else
    echo "PyTorch: not installed"
fi

echo ""
echo "サーバーを起動するには:"
echo "  python server/main.py"
echo ""
echo "エッジクライアントを起動するには:"
echo "  python edge/client.py --device-id jetson-001 --server-url http://SERVER_IP:8000"
echo ""
echo "環境を無効化するには:"
echo "  deactivate"
EOF
        chmod +x activate_jetson_env.sh
        
        # インストール検証
        echo "インストールを検証します..."
        echo "numpy: $(python -c 'import numpy; print(numpy.__version__)' 2>/dev/null || echo 'failed')"
        echo "opencv: $(python -c 'import cv2; print(cv2.__version__)' 2>/dev/null || echo 'failed')"
        echo "fastapi: $(python -c 'import fastapi; print("OK")' 2>/dev/null || echo 'failed')"
        echo "ultralytics: $(python -c 'import ultralytics; print(ultralytics.__version__)' 2>/dev/null || echo 'failed')"
        
        # 競合チェック
        numpy_ver=$(python -c "import numpy; print(numpy.__version__)" 2>/dev/null || echo "none")
        ultralytics_ver=$(python -c "import ultralytics; print(ultralytics.__version__)" 2>/dev/null || echo "none")
        
        if [[ "$numpy_ver" == "1.22."* || "$numpy_ver" == "1.2"[3-9]* ]] && [[ "$ultralytics_ver" == "8.0.2"* ]]; then
            echo "✅ numpy-ultralytics競合が解決されました！"
        else
            echo "⚠️  依存関係を確認してください: numpy=$numpy_ver, ultralytics=$ultralytics_ver"
        fi
        
        echo ""
        echo "✅ セットアップ完了！"
        echo "次回は以下のコマンドで環境をアクティベートしてください:"
        echo "  source activate_jetson_env.sh"
        ;;
        
    3)
        echo "=========================================="
        echo "互換版セットアップ (numpy 1.19.5)"
        echo "=========================================="
        
        # Python 3.8のインストール確認
        if ! command -v python3.8 &> /dev/null; then
            echo "Python 3.8をインストールします..."
            sudo apt update
            sudo apt install -y python3.8 python3.8-venv python3.8-dev python3.8-distutils
        fi
        
        # 互換版仮想環境の作成
        VENV_PATH="$HOME/venv-jetson-compat"
        echo "互換版仮想環境を作成します: $VENV_PATH"
        
        if [ -d "$VENV_PATH" ]; then
            echo "既存の仮想環境を削除します..."
            rm -rf "$VENV_PATH"
        fi
        
        python3.8 -m venv "$VENV_PATH"
        source "$VENV_PATH/bin/activate"
        
        echo "互換版環境のPython: $(python --version)"
        python -m pip install --upgrade pip
        
        # 古いnumpyから順番にインストール
        echo "互換版パッケージをインストールします..."
        python -m pip install "numpy==1.19.5"
        python -m pip install "opencv-python==4.5.1.48"
        python -m pip install "pillow==8.2.0"
        python -m pip install "fastapi==0.68.0"
        python -m pip install "uvicorn==0.15.0"
        python -m pip install "aiofiles==0.7.0"
        python -m pip install "requests==2.26.0"
        python -m pip install "python-dotenv==0.19.0"
        
        # 古いultralytics（numpy 1.19.5対応）
        echo "ultralytics (互換版) をインストールします..."
        python -m pip install "ultralytics==8.0.100"
        
        # 互換版アクティベーションスクリプト
        cat > activate_jetson_env.sh << 'EOF'
#!/bin/bash
# Jetson Nano互換版環境のアクティベート
export JETSON_ENV=compat
export CUDA_VISIBLE_DEVICES=0

VENV_PATH="$HOME/venv-jetson-compat"

if [ ! -f "$VENV_PATH/bin/activate" ]; then
    echo "エラー: 互換版仮想環境が見つかりません: $VENV_PATH"
    echo "setup_jetson.sh で選択肢3を再実行してください"
    return 1
fi

source "$VENV_PATH/bin/activate"

echo "🤖 互換版環境がアクティブになりました"
echo "Python: $(python --version)"

# パッケージバージョン確認
numpy_version=$(python -c "import numpy; print(numpy.__version__)" 2>/dev/null || echo "not installed")
ultralytics_version=$(python -c "import ultralytics; print(ultralytics.__version__)" 2>/dev/null || echo "not installed")

echo "numpy: $numpy_version (互換版)"
echo "ultralytics: $ultralytics_version (互換版)"

echo ""
echo "注意: これは互換性重視版です。一部の新機能は利用できません。"
echo ""
echo "サーバーを起動するには:"
echo "  python server/main.py"
echo ""
echo "環境を無効化するには:"
echo "  deactivate"
EOF
        chmod +x activate_jetson_env.sh
        
        echo ""
        echo "✅ 互換版セットアップ完了！"
        echo "次回は以下のコマンドで環境をアクティベートしてください:"
        echo "  source activate_jetson_env.sh"
        ;;
        
    4)
        echo "=========================================="
        echo "現在の環境での強制実行"
        echo "=========================================="
        
        echo "警告: Python $(python3 --version) での実行は互換性問題が発生する可能性があります"
        read -p "続行しますか？ [y/N]: " confirm
        
        if [[ $confirm == [yY] ]]; then
            echo "依存関係をインストールします..."
            
            # pipの確認
            if command -v pip3 &> /dev/null; then
                pip3 install --upgrade pip
                pip3 install -r requirements.txt || {
                    echo "requirements.txtでのインストールに失敗しました"
                    echo "個別パッケージのインストールを試行します..."
                    pip3 install fastapi uvicorn aiofiles requests
                }
            else
                echo "エラー: pip3が見つかりません"
                exit 1
            fi
            
            echo ""
            echo "セットアップ完了（互換性問題が発生する可能性があります）"
        else
            echo "セットアップを中止しました"
            exit 1
        fi
        ;;
        
    *)
        echo "無効な選択です"
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo "✅ セットアップ完了"
echo "=========================================="
echo ""
echo "次のステップ:"
echo "1. 環境変数の設定: cp .env.example .env"
echo "2. 設定の編集: nano .env"
if [ -f activate_jetson_env.sh ]; then
    echo "3. 環境のアクティベート: source activate_jetson_env.sh"
    echo "4. サーバーの起動: python server/main.py"
else
    echo "3. サーバーの起動: python server/main.py"
fi
echo ""
