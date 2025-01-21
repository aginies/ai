#!/bin/bash
# antoine@ginies.org
# For AMD GPU !
#set -exuo pipefail

export ROCMV=6.2
export PYBIN=python3.11
export SDW_DIR=/ComfyUI
export DIR_TO_CHECK=${SDW_DIR}/venv

start_server() {
	echo "Starting it:"
	echo "CCOMMANDLINE_ARGS:" ${OPTIONS}
	cd ${SDW_DIR}
	source ${DIR_TO_CHECK}/bin/activate
	echo "HSA_OVERRIDE_GFX_VERSION=11.0.0 PYTORCH_HIP_ALLOC_CONF=expandable_segments:True TORCH_ROCM_AOTRITON_ENABLE_EXPERIMENTAL=1 ${PYBIN} main.py ${OPTIONS}"
	HSA_OVERRIDE_GFX_VERSION=11.0.0 PYTORCH_HIP_ALLOC_CONF=expandable_segments:True TORCH_ROCM_AOTRITON_ENABLE_EXPERIMENTAL=1 ${PYBIN} main.py ${OPTIONS}
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
