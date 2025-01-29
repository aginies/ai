# Define the tags for OBS and build script builds:
#!BuildTag: %%TAGPREFIX%%/comfyui:latest
#!BuildTag: %%TAGPREFIX%%/comfyui:%%PKG_VERSION%%
#!BuildTag: %%TAGPREFIX%%/comfyui:%%PKG_VERSION%%-%RELEASE%

FROM registry.opensuse.org/opensuse/tumbleweed

# Mandatory labels for the build service:
#   https://en.opensuse.org/Building_derived_containers
# labelprefix=%%LABELPREFIX%%
LABEL Description="amdgpu_top Container"
LABEL org.opencontainers.image.title="amdgpu_top container"
LABEL org.opencontainers.image.description="amdgpu_top"
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
	amdgpu_top

#	cargo \
#	git \
#	libdrm-devel

#RUN git clone https://github.com/Umio-Yasuno/amdgpu_top.git
#RUN cd amdgpu_top/ \
#	&& cargo install --locked --path . --no-default-features --features="tui"

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
