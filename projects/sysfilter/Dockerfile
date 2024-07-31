FROM debian
LABEL org.opencontainers.image.authors="Sebastian Schirle"

ENV GIT_REPO="/sysfilter"
ENV GIT_REPO_URL="https://gitlab.com/Egalito/sysfilter"
# path to binary (when build)
ENV BIN="$GIT_REPO/extraction/app/build_x86_64/sysfilter_extract"

# install dependencies
RUN apt update
RUN apt install -y patchelf build-essential gdb libc6-dbg libreadline-dev lsb-release
RUN apt install -y git vim python3

# for tar support (analysis)dock
RUN apt install -y libnss-ldap
ADD /patches/nsswitch.conf /etc/

# clone repo
WORKDIR /
RUN git clone --recursive $GIT_REPO_URL

WORKDIR $GIT_REPO/extraction
# hot patch the DISTRO line
RUN sed -i "s/\$(word 3,\$(shell lsb_release -i))/\$(shell lsb_release -\s -i | cut -d \" \" -f 1)/g" egalito/env.mk

# build
RUN make -j$(nproc) all

# copy the scripts into the container
WORKDIR /testsuit/
RUN cp $BIN ./sysfilter.elf
# no support for relative paths in Dockerfile
# ADD --chmod=700 ../testsuit/build_bins.sh ./
ADD --chmod=700 testsuit/*.sh ./
ADD --chmod=700 *.sh ./

# build binaries
RUN ./build_bins.sh

WORKDIR /testsuit/
# run the testsuit
# RUN ./run_suit.sh