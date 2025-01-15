#!/bin/bash
# antoine@ginies.org
#set -exuo pipefail

# https://localai.io/features/image-generation/#configuration-parameters
# For AMD GPU skip CUDA test
export ROCMV=6.2
export HSA_OVERRIDE_GFX_VERSION=11.0.0
export HIP_VISIBLE_DEVICES=0
export PYBIN=python3.11

export SDW_DIR=/ComfyUI
export DIR_TO_CHECK=${SDW_DIR}/venv

start_server() {
	echo "Starting it:"
	echo "CCOMMANDLINE_ARGS:" ${OPTIONS}
	cd ${SDW_DIR}
	source ${DIR_TO_CHECK}/bin/activate
	HSA_OVERRIDE_GFX_VERSION=11.0.0 ${PYBIN} main.py ${OPTIONS}
}

# Check BUILD
if [ "$BUILD" = "true" ] || [ -z "$BUILD" ]; then
	echo "BUILD is true"
	echo "Directory ${DIR_TO_CHECK} not found ..."
	cd ${SDW_DIR}
	${PYBIN} -m venv venv
	source venv/bin/activate
	pip install --upgrade pip wheel
	pip3.11 install torch torchvision torchsde torchaudio --index-url https://download.pytorch.org/whl/rocm${ROCMV}
	pip3.11 install -r requirements.txt
	start_server
elif [ "$BUILD" = "debug" ] || [ -z "$BUILD" ]; then
	echo "To Debug it:"
	echo "docker exec -it comfyui /bin/bash"
	sleep infinity
else
	echo "BUILD is false. Starting comfyui"
	if [ ! -d "${DIR_TO_CHECK}" ]; then
		echo "Directory ${DIR_TO_CHECK} doesnt exists, will start debug mode..."
		echo "set BUILD=true in the docker-compose.yaml file"
		echo "To Debug from another terminal do:"
		echo "docker exec -it comfyui /bin/bash"
		echo "sleep infinity"
		sleep infinity
	fi
	start_server
fi
