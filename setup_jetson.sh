#!/bin/bash
"""
Jetson Nano環境セットアップスクリプト
JetPack 4.6.6 + Python 3.8環境の構築
"""

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

# 選択肢の提示
echo "セットアップ方法を選択してください:"
echo "1) Docker環境での実行 (推奨)"
echo "2) Python 3.8仮想環境のセットアップ"
echo "3) 現在のPython環境での強制実行 (非推奨)"
echo ""

read -p "選択してください [1-3]: " choice

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
        
        # Python 3.8のインストール
        echo "Python 3.8をインストールします..."
        sudo apt update
        sudo apt install -y python3.8 python3.8-venv python3.8-dev python3.8-distutils
        
        # 仮想環境の作成
        VENV_PATH="$HOME/venv-jetson-py38"
        echo "仮想環境を作成します: $VENV_PATH"
        python3.8 -m venv $VENV_PATH
        
        # 仮想環境のアクティベート
        source $VENV_PATH/bin/activate
        
        # pipのアップグレード
        pip install --upgrade pip
        
        # システムパッケージのインストール（OpenCV等）
        echo "システムパッケージをインストールします..."
        sudo apt install -y python3-opencv python3-numpy
        
        # PyTorch（Jetson用）のインストール
        echo "Jetson用PyTorchをインストールします..."
        # JetPack 4.6.6用PyTorch wheel
        wget https://nvidia.box.com/shared/static/fjtbno0vpo676a25cgvuqc1wty0fkkg6.whl -O torch-1.10.0-cp38-cp38-linux_aarch64.whl
        pip install torch-1.10.0-cp38-cp38-linux_aarch64.whl
        
        # torchvision
        sudo apt install -y libjpeg-dev zlib1g-dev
        git clone --branch v0.11.1 https://github.com/pytorch/vision torchvision
        cd torchvision
        python setup.py install
        cd ..
        rm -rf torchvision
        
        # その他の依存関係
        echo "プロジェクトの依存関係をインストールします..."
        pip install -r requirements-jetson.txt
        
        # 環境変数設定スクリプトの作成
        cat > activate_jetson_env.sh << 'EOF'
#!/bin/bash
# Jetson Nano環境のアクティベート
export JETSON_ENV=1
export CUDA_VISIBLE_DEVICES=0
source ~/venv-jetson-py38/bin/activate
echo "Jetson Nano Python 3.8環境がアクティブになりました"
echo "Python: $(python --version)"
echo "PyTorch: $(python -c 'import torch; print(torch.__version__)' 2>/dev/null || echo 'not installed')"
echo ""
echo "サーバーを起動するには:"
echo "  cd server && python main.py"
EOF
        chmod +x activate_jetson_env.sh
        
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
            pip3 install -r requirements.txt
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
