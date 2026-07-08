#!/usr/bin/env bash
# Check the host is ready for the ADVANCED (GPU) track.
set -uo pipefail

ok=0
echo "== NVIDIA driver =="
if command -v nvidia-smi >/dev/null 2>&1; then
    nvidia-smi --query-gpu=name,driver_version --format=csv,noheader
    DRV=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader | head -1 | cut -d. -f1)
    if [ "${DRV:-0}" -ge 580 ]; then
        echo "  driver ${DRV} >= 580  ->  Jazzy + cuMotion 4.5 OK"
    else
        echo "  driver ${DRV} < 580  ->  use the Humble + cuMotion 3.2 fallback (docs/02_install_gpu.md)"
        ok=1
    fi
else
    echo "  nvidia-smi not found (no NVIDIA driver?). CORE track only."
    ok=1
fi

echo "== nvidia-container-toolkit =="
if docker info 2>/dev/null | grep -qi nvidia; then
    echo "  nvidia runtime available"
else
    echo "  nvidia runtime NOT configured. Install nvidia-container-toolkit:"
    echo "    sudo apt-get install -y nvidia-container-toolkit"
    echo "    sudo nvidia-ctk runtime configure --runtime=docker && sudo systemctl restart docker"
    ok=1
fi

echo "== GPU visible in a container =="
if docker run --rm --gpus all nvidia/cuda:12.4.0-base-ubuntu22.04 nvidia-smi -L >/dev/null 2>&1; then
    echo "  GPU passthrough works"
else
    echo "  could not run a GPU container (check toolkit / permissions)"
    ok=1
fi

[ "$ok" -eq 0 ] && echo "READY for the advanced track." || echo "Advanced track not ready; CORE track still works."
exit 0
