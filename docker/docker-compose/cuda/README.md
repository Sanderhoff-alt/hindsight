# Hindsight with NVIDIA CUDA GPU Acceleration

Example setup that builds a custom Hindsight image with **CUDA-enabled PyTorch**
for NVIDIA GPU-accelerated local embeddings and reranking.

## When to use this

- You want to use in-process local embeddings (`HINDSIGHT_API_EMBEDDINGS_PROVIDER: local`)
  and reranking (`HINDSIGHT_API_RERANKER_PROVIDER: local`) with NVIDIA GPU acceleration.
- You want lower latency and higher throughput for local embedding and reranker inference.
- You have an NVIDIA GPU and want to run Hindsight locally without external TEI sidecars.

> [!NOTE]
> This accelerates Hindsight's in-process PyTorch embedding and reranker models.
> The LLM (used for retain/recall/reflect) is external by default (e.g. OpenAI, Anthropic, Ollama, vLLM).

## Prerequisites

1. **Linux x86_64 (`linux/amd64`) host**: The CUDA PyTorch runtime in this recipe targets NVIDIA x86_64 platforms.
2. **NVIDIA GPU** with compatible driver (driver version `>= 525.60.13` recommended for CUDA 12.x).
3. **[NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)**
   installed and configured on the host Docker daemon.

Verify GPU access in Docker:
```bash
docker run --rm --gpus all nvidia/cuda:12.6.0-base-ubuntu22.04 nvidia-smi
```

## Quick start

```bash
export HINDSIGHT_API_LLM_API_KEY=sk-xxx

docker compose -f docker/docker-compose/cuda/docker-compose.yaml up --build
```

- API: http://localhost:8888
- Control Plane: http://localhost:9999

## Building manually

You can also build the image directly using `docker build`:

```bash
docker build -f docker/docker-compose/cuda/Dockerfile -t hindsight:cuda .
```

Then run the container with GPU passthrough:

```bash
docker run --gpus all \
  --name hindsight-cuda \
  -p 8888:8888 -p 9999:9999 \
  -e HINDSIGHT_API_LLM_API_KEY=sk-xxx \
  hindsight:cuda
```

## Verifying CUDA GPU Acceleration

When Hindsight starts, check the container logs to ensure CUDA is detected:

```bash
docker logs hindsight-cuda | grep -i "device"
```

Both embedding and cross-encoder log lines will report `device: cuda` instead of `device: cpu`.
