FROM ubuntu
LABEL org.opencontainers.image.authors="Sebastian Schirle"

ENV GIT_REPO="/chestnut"
ENV GIT_REPO_URL="https://github.com/IAIK/Chestnut.git"

# install dependencies
RUN apt update
# binalyzer
RUN apt install -y vim build-essential pip python3 python3-venv
# sourcealyzer
RUN apt install -y git cmake make ninja-build clang seccomp wget gperf
# dynalyzer
RUN apt install -y clang wget gperf

ADD $GIT_REPO_URL $GIT_REPO/

# Binalyzer
# --------- 
ENV BA="$GIT_REPO/Binalyzer"
WORKDIR $BA
ENV binalyzer="$BA/filter.py"

# create and enable venv
RUN python3 -m venv /venv/
ENV PATH="/venv/bin:$PATH"
# install dependencies
RUN pip install -r requirements.txt
# fix missing dependency
RUN pip install setuptools
# fix broken files (adapt for more drops)
ADD patches/*.py ./

# Sourcealyzer
# ------------
ENV SA="$GIT_REPO/Sourcealyzer"
WORKDIR $SA

# need to fix seccomp (missing a lot of dependencies)
ADD https://github.com/seccomp/libseccomp/releases/download/v2.5.5/libseccomp-2.5.5.tar.gz ./
RUN tar -xzf libseccomp-2.5.5.tar.gz
WORKDIR $SA/libseccomp-2.5.5
RUN ./configure
RUN make -j$(nproc)
RUN make install

WORKDIR $SA
# split becasue I need to insert the patches inbetween
# RUN ./download_and_build.sh
ADD --chmod=700 patches/*.sh ./
# download and build
RUN ./d_n_b.sh
# fix broken imports
RUN sed -i 's/#include <string>/#include <string>\n#include <cstdint>/g' /chestnut/Sourcealyzer/llvm10/llvm/include/llvm/Support/Signals.h 
RUN sed -i 's/#include <vector>/#include <vector>\n#include <limits>/g' /chestnut/Sourcealyzer/llvm10/llvm/utils/benchmark/src/benchmark_register.h 
# add clang to the build list
RUN cp -r llvm10/clang/ llvm10/llvm/tools/
# add clang to the build list
RUN cp -r llvm10/lld/ llvm10/llvm/tools/
# patch and build
RUN ./p_n_b.sh

ENV llvm_dir="$SA/llvm10/build/bin/"

# Dynalyzer
# -----------
ENV DA="$GIT_REPO/Dynalyzer"
WORKDIR $DA 
RUN make all -j$(nproc)

# run the testsuit (Binalyzer)
# ----------------------------
WORKDIR /testsuit/ba
ADD --chmod=700 testsuit/build_tools.sh ./
RUN ./build_tools.sh

# run the testsuit (Sourcealyzer)
# ----------------------------
WORKDIR /testsuit/sa
ADD --chmod=700 testsuit/clone_tools.sh ./
RUN ./clone_tools.sh

# for manual interaction
WORKDIR /testsuit/
ADD --chmod=700 *run.sh ./
ADD --chmod=700 testsuit/*suit.sh ./
