#!/bin/bash
# antoine@ginies.org
#set -exuo pipefail

export PYBIN=python3.11
export SDW_DIR=/ComfyUI
export DIR_TO_CHECK=${SDW_DIR}/venv

start_server() {
	echo "Starting it:"
	echo "CCOMMANDLINE_ARGS:" ${OPTIONS}
	cd ${SDW_DIR}
	source ${DIR_TO_CHECK}/bin/activate
	if [ "$GPU" = "AMD" ]; then
		echo "HSA_OVERRIDE_GFX_VERSION=${GFX} PYTORCH_HIP_ALLOC_CONF=expandable_segments:True TORCH_ROCM_AOTRITON_ENABLE_EXPERIMENTAL=1 ${PYBIN} main.py ${OPTIONS}"
		HSA_OVERRIDE_GFX_VERSION=${GFX} PYTORCH_HIP_ALLOC_CONF=expandable_segments:True TORCH_ROCM_AOTRITON_ENABLE_EXPERIMENTAL=1 ${PYBIN} main.py ${OPTIONS}
	elif [ "$GPU" = "AMDZLUDA" ] || [ "$GPU" = "NVIDIA" ]; then
		echo "PYTORCH_HIP_ALLOC_CONF=expandable_segments:True TORCH_ROCM_AOTRITON_ENABLE_EXPERIMENTAL=1 ${PYBIN} main.py ${OPTIONS}"
		PYTORCH_HIP_ALLOC_CONF=expandable_segments:True TORCH_ROCM_AOTRITON_ENABLE_EXPERIMENTAL=1 ${PYBIN} main.py ${OPTIONS}
	fi
}

if [ "$BUILD" = "debug" ] || [ -z "$BUILD" ]; then
	echo "To Debug it:"
	echo "docker exec -it comfyui /bin/bash"
	sleep infinity
else
	echo "BUILD is false. Starting comfyui"
	# check that the directory is present
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
