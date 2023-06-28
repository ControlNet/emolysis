#/bin/bash

ENV_NAME=${1:-emolysis}

conda create -y -n $ENV_NAME python=3.9
conda activate $ENV_NAME
conda install -y -c conda-forge cudatoolkit=11.2 cudnn=8.1.0
conda install -y ffmpeg

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$CONDA_PREFIX/lib/

pip install tensorflow==2.9.1
pip install torch==1.11.0+cu113 torchvision==0.12.0+cu113 torchaudio==0.11.0 --extra-index-url https://download.pytorch.org/whl/cu113
pip install pyzmq==24.0.1 tensorneko==0.2.7 transformers==4.24.0 hsemotion==0.2 facenet_pytorch==2.5.2 tensorflow_hub==0.12.0 pydub==0.25.1 librosa==0.9.2 BeautifulSoup4==4.11.1 moviepy==1.0.3 lxml==4.9.1 pandas==1.3.5 fastapi==0.89.0 starlette==0.22.0 uvicorn==0.20.0 websockets==10.4 python-multipart==0.0.5 timm==0.6.13
pip install git+https://github.com/openai/whisper.git
