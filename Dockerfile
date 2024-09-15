FROM pytorch/pytorch:1.13.1-cuda11.6-cudnn8-runtime

EXPOSE 8000

WORKDIR /app

RUN apt update
RUN apt install -y ffmpeg git
RUN pip install "pip<24.1"
RUN /opt/conda/bin/conda init bash
RUN pip install tensorflow==2.9.1
RUN pip install torchvision==0.14.1 torchaudio==0.13.1 torch==1.13.1 numpy==1.26.4 numba==0.60.0 pyzmq==24.0.1 tensorneko==0.2.7 transformers==4.24.0 hsemotion==0.3 facenet_pytorch==2.5.2 tensorflow_hub==0.12.0 pydub==0.25.1 librosa==0.9.2 BeautifulSoup4==4.11.1 moviepy==1.0.3 lxml==4.9.1 pandas==1.3.5 fastapi==0.89.0 starlette==0.22.0 uvicorn==0.20.0 websockets==10.4 python-multipart==0.0.5 timm==0.9.7 torchmetrics==0.11.4
RUN pip install openai_whisper==20231117

COPY . .

RUN pip cache purge
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

ENV LD_LIBRARY_PATH=/opt/conda/lib
ENV TF_FORCE_GPU_ALLOW_GROWTH=true

ENTRYPOINT ["/opt/conda/bin/python", "service/main.py", "--port", "8000"]
