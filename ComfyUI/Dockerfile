# Define the tags for OBS and build script builds:
#!BuildTag: %%TAGPREFIX%%/comfyui:latest
#!BuildTag: %%TAGPREFIX%%/comfyui:%%PKG_VERSION%%
#!BuildTag: %%TAGPREFIX%%/comfyui:%%PKG_VERSION%%-%RELEASE%

FROM registry.opensuse.org/opensuse/leap:15.6

# Mandatory labels for the build service:
#   https://en.opensuse.org/Building_derived_containers
# labelprefix=%%LABELPREFIX%%
LABEL Description="comfyui Container"
LABEL org.opencontainers.image.title="comfyui container"
LABEL org.opencontainers.image.description="Container for comfyui"
LABEL org.opencontainers.image.created="%BUILDTIME%"
LABEL org.opencontainers.image.version="%%PKG_VERSION%%.%RELEASE%"
LABEL org.openbuildservice.disturl="%DISTURL%"
LABEL org.opensuse.reference="%%REGISTRY%%/%%TAGPREFIX%%/comfyui:%%PKG_VERSION%%.%RELEASE%"
LABEL org.openbuildservice.disturl="%DISTURL%"
LABEL com.suse.supportlevel="techpreview"
LABEL com.suse.eula="beta"
LABEL com.suse.image-type="application"
LABEL com.suse.release-stage="prototype"
# endlabelprefix

# Install needed software
RUN zypper install --no-recommends -y \
	python311-pip \
	git \
	libtcmalloc4 \
	libglvnd \
	python311-aiosqlite \
	libtcmalloc4 \
	libglvnd \
	libgthread-2_0-0 

# Grab comfyui and clone needed repo in the container
# https://github.com/comfyanonymous/ComfyUI.git
RUN git clone https://github.com/comfyanonymous/ComfyUI.git
RUN cd ComfyUI \
	&& python3.11 -m venv venv \
	&& source venv/bin/activate \
	&& pip install --upgrade pip wheel \
	&& pip3.11 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm6.2 \
	&& pip install -r requirements.txt \
	&& cd custom_nodes \
	&& git clone https://github.com/ltdrdata/ComfyUI-Manager comfyui-manager \
	&& git clone https://github.com/romeobuilderotti/ComfyUI-PNG-Metadata ComfyUI-PNG-Metadata 


#	&& HSA_OVERRIDE_GFX_VERSION=11.0.0 python3.11 main.py
#	&& TORCH_ROCM_AOTRITON_ENABLE_EXPERIMENTAL=1 python main.py --use-pytorch-cross-attention

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
