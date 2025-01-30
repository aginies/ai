# Define the tags for OBS and build script builds:
#!BuildTag: %%TAGPREFIX%%/comfyui:latest
#!BuildTag: %%TAGPREFIX%%/comfyui:%%PKG_VERSION%%
#!BuildTag: %%TAGPREFIX%%/comfyui:%%PKG_VERSION%%-%RELEASE%

FROM registry.opensuse.org/opensuse/leap:15.6

# Mandatory labels for the build service:
#   https://en.opensuse.org/Building_derived_containers
# labelprefix=%%LABELPREFIX%%
LABEL Description="ComfyUI AMD Container"
LABEL org.opencontainers.image.title="ComfyUI AMD container"
LABEL org.opencontainers.image.description="Container for ComfyUI AMD"
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
	libglvnd \
	python311-aiosqlite \
	libtcmalloc4 \
	xorg-x11-fonts \
	libglvnd \
	libgthread-2_0-0 

# Grab comfyui and clone needed repo in the container
# https://github.com/comfyanonymous/ComfyUI.git
RUN git clone https://github.com/comfyanonymous/ComfyUI.git
RUN cd ComfyUI \
	&& python3.11 -m venv venv \
	&& source venv/bin/activate \
	&& pip install --upgrade pip wheel \
	&& pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/rocm6.3 \
	&& pip install -r requirements.txt \
	&& pip install -r https://github.com/comfyanonymous/ComfyUI/raw/refs/heads/master/requirements.txt -r https://github.com/ltdrdata/ComfyUI-Manager/raw/refs/heads/main/requirements.txt -r https://raw.githubusercontent.com/city96/ComfyUI_ExtraModels/refs/heads/main/requirements.txt -r https://raw.githubusercontent.com/Fannovel16/comfyui_controlnet_aux/refs/heads/main/requirements.txt -r https://raw.githubusercontent.com/pythongosssss/ComfyUI-WD14-Tagger/refs/heads/main/requirements.txt -r https://raw.githubusercontent.com/Stability-AI/stability-ComfyUI-nodes/refs/heads/master/requirements.txt

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
