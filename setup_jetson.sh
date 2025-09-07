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
echo "⚠️  依存関係競合の解決オプション"
echo "numpy バージョン競合が検出される場合があります。"
echo ""
echo "セットアップ方法を選択してください:"
echo "1) Docker環境での実行 (最推奨・競合なし)"
echo "2) numpy更新版 - Python 3.8仮想環境"
echo "3) 互換版 - 古いnumpyを維持"
echo "4) 現在のPython環境での強制実行 (非推奨)"
echo ""

read -p "選択してください [1-4]: " choice

case $choice in
    1)
        echo "=========================================="
        echo "Docker環境のセットアップ"
        echo "=========================================="
        
        # Docker環境の設定（既存のコード）
        # ...
        
    2)
        echo "=========================================="
        echo "Python 3.8仮想環境 (numpy更新版)"
        echo "=========================================="
        
        # Python 3.8仮想環境のセットアップ
        VENV_PATH="$HOME/venv-jetson-py38"
        
        if [ -d "$VENV_PATH" ]; then
            echo "既存の仮想環境を削除します..."
            rm -rf "$VENV_PATH"
        fi
        
        python3.8 -m venv "$VENV_PATH"
        source "$VENV_PATH/bin/activate"
        
        # pip を更新
        pip install --upgrade pip
        
        # numpy を先にアップデート
        echo "📦 numpy バージョンを更新して競合を解決しています..."
        pip install "numpy>=1.22.2"
        
        # 他の依存関係をインストール
        pip install -r requirements-jetson.txt
        
        echo "✅ セットアップ完了"
        ;;
    
    3)
        echo "=========================================="
        echo "Python 3.8仮想環境 (互換版)"
        echo "=========================================="
        
        # Python 3.8仮想環境のセットアップ
        VENV_PATH="$HOME/venv-jetson-py38-compat"
        
        if [ -d "$VENV_PATH" ]; then
            echo "既存の仮想環境を削除します..."
            rm -rf "$VENV_PATH"
        fi
        
        python3.8 -m venv "$VENV_PATH"
        source "$VENV_PATH/bin/activate"
        
        # pip を更新
        pip install --upgrade pip
        
        # 互換版依存関係をインストール
        echo "📦 互換版パッケージをインストールしています..."
        pip install -r requirements-jetson-compat.txt
        
        echo "✅ セットアップ完了"
        ;;
    
    4) then
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
                pip install -r requirements-jetson.txt
                echo 'Setup completed!'
                echo 'Run: python3 server/main.py to start the server'
                bash
            "
        ;;
        
    2)
        echo "=========================================="
        echo "Python 3.8仮想環境のセットアップ"
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
        
        # システムパッケージのインストール（OpenCV等）
        echo "システムパッケージをインストールします..."
        sudo apt install -y python3-opencv python3-numpy libopencv-dev
        
        # PyTorch（Jetson用）のインストール
        echo "Jetson用PyTorchをインストールします..."
        # JetPack 4.6.6用PyTorch wheel
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
        
        # その他の依存関係
        echo "プロジェクトの依存関係をインストールします..."
        
        # requirements-jetson.txtが存在するかチェック
        if [ -f "requirements-jetson.txt" ]; then
            python -m pip install -r requirements-jetson.txt
        elif [ -f "requirements.txt" ]; then
            echo "requirements-jetson.txtが見つからないため、requirements.txtを使用します"
            python -m pip install -r requirements.txt
        else
            echo "警告: requirements ファイルが見つかりません"
        fi
        
        # 環境変数設定スクリプトの作成
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

echo "Jetson Nano Python 3.8環境がアクティブになりました"
echo "Python: $(python --version)"
echo "pip: $(pip --version)"

# PyTorchの確認
if python -c "import torch" 2>/dev/null; then
    echo "PyTorch: $(python -c 'import torch; print(torch.__version__)')"
    echo "CUDA Available: $(python -c 'import torch; print(torch.cuda.is_available())')"
else
    echo "PyTorch: not installed"
fi

echo ""
echo "サーバーを起動するには:"
echo "  cd $(pwd) && python server/main.py"
echo ""
echo "環境を無効化するには:"
echo "  deactivate"
EOF
        chmod +x activate_jetson_env.sh
        
        # インストール検証
        echo "インストールを検証します..."
        if python -c "import torch, cv2, fastapi" 2>/dev/null; then
            echo "✓ 主要パッケージのインポートに成功"
        else
            echo "⚠ 一部のパッケージでインポートエラーが発生しました"
        fi
        
        echo ""
        echo "セットアップ完了！"
        echo "次回は以下のコマンドで環境をアクティベートしてください:"
        echo "  source activate_jetson_env.sh"
        ;;
        
    3)
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
echo "セットアップ完了"
echo "=========================================="
echo ""
echo "次のステップ:"
echo "1. 環境変数の設定: cp .env.example .env"
echo "2. 設定の編集: nano .env"
echo "3. サーバーの起動: python server/main.py"
echo ""
