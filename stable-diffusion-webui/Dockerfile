# Define the tags for OBS and build script builds:
#!BuildTag: %%TAGPREFIX%%/stable-diffusion-webui:latest
#!BuildTag: %%TAGPREFIX%%/stable-diffusion-webui:%%PKG_VERSION%%
#!BuildTag: %%TAGPREFIX%%/stable-diffusion-webui:%%PKG_VERSION%%-%RELEASE%

FROM registry.opensuse.org/opensuse/leap:15.6

# Mandatory labels for the build service:
#   https://en.opensuse.org/Building_derived_containers
# labelprefix=%%LABELPREFIX%%
LABEL Description="stable-diffusion-webui Container"
LABEL org.opencontainers.image.title="stable-diffusion-webui container"
LABEL org.opencontainers.image.description="Container for stable-diffusion-webui"
LABEL org.opencontainers.image.created="%BUILDTIME%"
LABEL org.opencontainers.image.version="%%PKG_VERSION%%.%RELEASE%"
LABEL org.openbuildservice.disturl="%DISTURL%"
LABEL org.opensuse.reference="%%REGISTRY%%/%%TAGPREFIX%%/stable-diffusion-webui:%%PKG_VERSION%%.%RELEASE%"
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

# for webui.sh you need also: pciutils, bc
# can be usefull: vim

# Grab stable-diffusion-webui-amdgpu and clonde needed repo in the container
# https://github.com/AUTOMATIC1111/stable-diffusion-webui
# https://github.com/lshqqytiger/stable-diffusion-webui-amdgpu
#RUN git clone --branch v1.10.1-amd https://github.com/lshqqytiger/stable-diffusion-webui-amdgpu.git stable-diffusion-webui
#RUN git clone https://github.com/lshqqytiger/stable-diffusion-webui-amdgpu.git stable-diffusion-webui
RUN git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui
RUN cd stable-diffusion-webui \
	&& python3.11 -m venv venv \
	&& source venv/bin/activate \
	&& pip install --upgrade pip wheel \
	&& pip3.11 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm6.2
#	&& . venv/bin/activate && python -c "from modules.launch_utils import prepare_environment; prepare_environment()"

#	&& mkdir repositories \
#	&& cd repositories \
#	&& git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui-assets.git \
#	&& git clone https://github.com/Stability-AI/stablediffusion.git \
#	&& git clone https://github.com/Stability-AI/generative-models.git \
#	&& git clone https://github.com/crowsonkb/k-diffusion.git \
#	&& pip3.11 install https://github.com/openai/CLIP/archive/d50d76daa670286dd6cacf3bcd80b5e4823fc8e1.zip \
#	&& pip3.11 install https://github.com/mlfoundations/open_clip/archive/bb6e834e9c70d9c27d0dc3ecedeebeaeb1ffad6b.zip \
#	&& git clone https://github.com/salesforce/BLIP.git 


COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
