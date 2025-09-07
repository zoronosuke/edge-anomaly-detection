#!/bin/bash
# Jetson環境のセットアップ確認テストスクリプト

echo "=========================================="
echo "Jetson環境セットアップ確認テスト"
echo "=========================================="

VENV_PATH="$HOME/venv-jetson-py38"

# 仮想環境の存在確認
if [ -d "$VENV_PATH" ]; then
    echo "✓ 仮想環境が存在します: $VENV_PATH"
    
    if [ -f "$VENV_PATH/bin/activate" ]; then
        echo "✓ activateスクリプトが存在します"
        
        # 仮想環境のアクティベート
        source "$VENV_PATH/bin/activate"
        
        echo "✓ 仮想環境がアクティベートされました"
        echo "  Python: $(python --version)"
        echo "  pip: $(pip --version)"
        
        # 主要パッケージのテスト
        echo ""
        echo "パッケージテスト:"
        
        # Python標準ライブラリ
        if python -c "import sys; print('Python executable:', sys.executable)" 2>/dev/null; then
            echo "✓ Python環境: OK"
        else
            echo "✗ Python環境: ERROR"
        fi
        
        # PyTorch
        if python -c "import torch; print('PyTorch version:', torch.__version__)" 2>/dev/null; then
            echo "✓ PyTorch: OK"
            if python -c "import torch; print('CUDA available:', torch.cuda.is_available())" 2>/dev/null; then
                echo "  CUDA support: $(python -c 'import torch; print(torch.cuda.is_available())')"
            fi
        else
            echo "✗ PyTorch: ERROR or not installed"
        fi
        
        # OpenCV
        if python -c "import cv2; print('OpenCV version:', cv2.__version__)" 2>/dev/null; then
            echo "✓ OpenCV: OK"
        else
            echo "✗ OpenCV: ERROR or not installed"
        fi
        
        # FastAPI
        if python -c "import fastapi; print('FastAPI version:', fastapi.__version__)" 2>/dev/null; then
            echo "✓ FastAPI: OK"
        else
            echo "✗ FastAPI: ERROR or not installed"
        fi
        
        # Uvicorn
        if python -c "import uvicorn; print('Uvicorn version:', uvicorn.__version__)" 2>/dev/null; then
            echo "✓ Uvicorn: OK"
        else
            echo "✗ Uvicorn: ERROR or not installed"
        fi
        
        # Ultralytics (YOLO)
        if python -c "import ultralytics; print('Ultralytics version:', ultralytics.__version__)" 2>/dev/null; then
            echo "✓ Ultralytics: OK"
        else
            echo "✗ Ultralytics: ERROR or not installed"
        fi
        
        deactivate
        
    else
        echo "✗ activateスクリプトが見つかりません"
    fi
    
else
    echo "✗ 仮想環境が見つかりません: $VENV_PATH"
    echo "  setup_jetson.shを実行してください"
fi

# activate_jetson_env.shの確認
echo ""
if [ -f "activate_jetson_env.sh" ]; then
    echo "✓ activate_jetson_env.sh が存在します"
    if [ -x "activate_jetson_env.sh" ]; then
        echo "✓ 実行権限があります"
    else
        echo "⚠ 実行権限がありません (chmod +x activate_jetson_env.sh を実行してください)"
    fi
else
    echo "✗ activate_jetson_env.sh が見つかりません"
fi

echo ""
echo "=========================================="
echo "テスト完了"
echo "=========================================="
echo ""
echo "使用方法:"
echo "1. 仮想環境のアクティベート: source activate_jetson_env.sh"
echo "2. サーバーの起動: python server/main.py"
echo "3. 環境の無効化: deactivate"
