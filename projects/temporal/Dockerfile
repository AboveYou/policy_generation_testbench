FROM ubuntu
LABEL org.opencontainers.image.authors="Sebastian Schirle"

RUN apt-get update
# install dependencies
# RUN apt-get install -y python3 git gcc g++ texinfo wget make bzip2 libgmp-dev libmpfr-dev xz-utils cmake
RUN apt-get install -y libedit-dev libncurses5-dev python3-dev cmake build-essential libncurses5-dev cmake git wget libgmp-dev libmpfr-dev texinfo

ENV ROOT="/"
ENV RESULTS="/results"

# clone temporal (project base root)
WORKDIR $ROOT
ENV TEMPORLA_DIR="$ROOT/temporal"

RUN git clone https://github.com/shamedgh/temporal-specialization temporal
WORKDIR $TEMPORLA_DIR
RUN git submodule update --init --recursive

# clone LLVM gold (included in bunutils)
WORKDIR $ROOT
ENV LLVM_GOLD_DIR="$ROOT/binutils/build"

RUN git clone --depth 1 git://sourceware.org/git/binutils-gdb.git binutils

# requirement: install M4
WORKDIR $LLVM_GOLD_DIR
RUN wget https://ftp.gnu.org/gnu/m4/m4-1.4.19.tar.gz
RUN tar zxf m4-1.4.19.tar.gz
WORKDIR $LLVM_GOLD_DIR/m4-1.4.19
RUN ./configure
RUN make install

# requirement: install bison
WORKDIR $LLVM_GOLD_DIR
RUN wget https://ftp.gnu.org/gnu/bison/bison-3.8.tar.gz
RUN tar zxf bison-3.8.tar.gz
WORKDIR $LLVM_GOLD_DIR/bison-3.8
RUN ./configure
RUN make install

# build LLVM plugin
WORKDIR $LLVM_GOLD_DIR
RUN ../configure --enable-gold --enable-plugins --disable-werror
RUN make all-gold

# build LLVM
WORKDIR $ROOT
ENV LLVM_DIR="$TEMPORLA_DIR/llvm-7.0.0.src/build"

# the zip comes with the repo
# RUN wget https://releases.llvm.org/7.0.0/llvm-7.0.0.src.tar.xz
WORKDIR $TEMPORLA_DIR
RUN tar -Jxvf llvm-7.0.0.src.wclang.tar.xz  
WORKDIR $LLVM_DIR

RUN cmake -G "Unix Makefiles" -DLLVM_BINUTILS_INCDIR="$ROOT/binutils/include/" -DLLVM_TARGETS_TO_BUILD="X86" -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=../install ../
RUN make -j$(nproc) && make install
ENV PATH="$LLVM_DIR/bin:$PATH"

# build SVF (callgraph binaries)
ENV SVF_DIR="$TEMPORLA_DIR/SVF/Release-build"
WORKDIR $TEMPORLA_DIR/SVF

RUN ./build.sh
ENV PATH="$SVF_DIR/bin:$PATH"

# avoid error command when configuring
ENV FORCE_UNSAFE_CONFIGURE=1

# NGINX example
# this will take about 15min
# RUN wget https://nginx.org/download/nginx-1.22.1.tar.gz
# RUN tar zxf nginx-1.22.1.tar.gz
# WORKDIR /binary/nginx-1.22.11
# RUN CC=clang CXX=clang++ LD=/usr/bin/ld CFLAGS="-flto -O0" ./configure --with-ld-opt="-flto -Wl,-plugin-opt=save-temps" --without-http_rewrite_module --without-http_gzip_module
# RUN make
# RUN cp objs/nginx.0.5.precodegen.bc ../
# RUN cp objs/nginx ../
# WORKDIR /binary
# RUN ./extract_syscalls.sh ./nginx.0.5.precodegen.bc /project/temporal/

# adding scripts
WORKDIR /testsuit/
ADD --chmod=700 testsuit/* ./
RUN ./clone_tools.sh

# testsuit
ADD --chmod=700 *.sh ./