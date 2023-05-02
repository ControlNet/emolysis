# Emolysis

This repo is official repository for the paper [Emolysis: A Group Emotion Analysis Toolkit for ‘in-the-wild’ Videos]().

## Get Started

We provided a static demo review for you to try. Please visit [https://emolysis.controlnet.space/local/1](https://emolysis.controlnet.space/local/1).

If you want to analyze your own video, please follow the instructions below.

## Deploy the Server

### From Docker

Requires:
- Docker
- nvidia-docker

Run the server.
```bash
docker run --runtime nvidia -p <PORT>:8000 controlnet/emolysis
```

Then, you can access the app at `http://127.0.0.1:<PORT>`.

### From Source

Requires:
- Conda
- Node.js

Install dependencies.
```bash
npm install
npm run build
cd service
bash -i build_env.sh
conda activate emolysis
cd ..
```

Run the server.
```bash
python service/main.py <PORT>
```

Then, you can access the app at `http://127.0.0.1:<PORT>`.
