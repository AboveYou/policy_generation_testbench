FROM debian
LABEL org.opencontainers.image.authors="Sebastian Schirle"

ENV GIT_REPO="/fuzzypol"
#  currently the private
ENV GIT_REPO_URL="https://gitlab.com/iot-aalen/fuzz-seccomp-filter.git"

# for AFL++ 
ENV IS_DOCKER=1
ENV AFL_I_DONT_CARE_ABOUT_MISSING_CRASHES=1
ENV AFL_SKIP_CPUFREQ=1

# copy the git repo
WORKDIR $GIT_REPO/
ADD policyFuzzing/ ./

# install dependencies
RUN apt update --fix-missing
RUN apt install -y build-essential dkms ansible-core 
RUN apt install -y pip python3 python3-venv git gawk
# RUN apt remove -y llvm-17 llvm-18

# create and enable venv
RUN python3 -m venv /venv/
ENV PATH="/venv/bin:$PATH"

# I initally patched the playbooks, this is deprecated now
# all the command from the playbook (and the patches are done below)
# WORKDIR $GIT_REPO/provisioning
# ADD patches/*.yml $GIT_REPO/provisioning/

# normal command for the playbooks
# RUN ansible-playbook -i inventory master_playbook.yml

# Master Playbook
# ---------------
# install dependencies
RUN apt install -y auditd afl++
# fix python installs
RUN pip install pyseccomp BitVector cffi pytest
# some more dependencies
RUN apt install -y libaudit-dev libauparse-dev python3-audit libseccomp-dev cmake bpfcc-tools
# linux-headers-$(uname -r)
# moving the plugin
RUN gcc $GIT_REPO/src/syscall_finder_plugin/audisp-plugin.c -o /usr/local/sbin/sbp-audisp-plugin -laudit -lauparse
# cmake for file-finder
RUN cmake $GIT_REPO/src/fileFinder -B $GIT_REPO/fileFinder
# build file-finder
RUN make -j$(nproc) -C $GIT_REPO/fileFinder
# install the plugin
RUN python3 $GIT_REPO/src/fileFinder/installConfigFile.py $GIT_REPO/fileFinder/AudispPlugin
# change configuration
RUN chown root:root /etc/audit/plugins.d/AudispPlugin.conf
RUN chmod 0640 /etc/audit/plugins.d/AudispPlugin.conf
# move config
RUN cp $GIT_REPO/src/syscall_finder_plugin/syscall_finder_config/sbp.conf /etc/audit/plugins.d/
RUN chown root:root /etc/audit/plugins.d/sbp.conf
# RUN chmod g-w o-r /etc/audit/plugins.d/sbp.conf
# moving fuzzing plugin
RUN cp $GIT_REPO/src/audisp_plugins/fuzzing_plugin.py /usr/local/sbin/fuzzing_plugin.py
RUN chown root:root /usr/local/sbin/fuzzing_plugin.py
RUN chmod 0755 /usr/local/sbin/fuzzing_plugin.py
# seccomp plugin
RUN cp $GIT_REPO/src/audisp_plugins/syscall_logger.py  /usr/local/sbin/syscall_logger.py
RUN chown root:root /usr/local/sbin/syscall_logger.py
RUN chmod 0755 /usr/local/sbin/syscall_logger.py 
# create fuzzing dirs
WORKDIR /fuzzing/in/
WORKDIR /fuzzing/out/
# replacing priority boost duditd
RUN sed 's/^(.*)priority_boost =(.*)\$/priority_boost = 10/' /etc/audit/auditd.conf
# increasing duditd queue depth
RUN sed 's/^(.*)q_depth =(.*)\$/q_depth = 1000/' /etc/audit/auditd.conf
# install bubblewrap
RUN apt install -y bubblewrap
# install glibc
WORKDIR $GIT_REPO/src/customGLIBC
RUN chmod u+x custom_glibc_install.sh
RUN ./custom_glibc_install.sh


# KLEE installation
# -----------------
# install dependencies
RUN apt install -y build-essential cmake curl file g++-multilib gcc-multilib git libcap-dev libgoogle-perftools-dev libncurses5-dev libsqlite3-dev libtcmalloc-minimal4 unzip graphviz doxygen
# install pip dependendies 
RUN pip install wllvm lit setuptools
# install llvm version
RUN apt install -y clang-14 llvm-14 llvm-14-dev llvm-14-tools z3
# Google Test Suite
WORKDIR /klee_installation_dir
ADD https://github.com/google/googletest/archive/release-1.11.0.zip ./
RUN unzip release-1.11.0.zip
# uClibc and POSIX environment model
WORKDIR /klee_installation_dir/klee-uclibc/
ADD https://github.com/klee/klee-uclibc.git ./
# configure and building uClic
RUN ./configure --make-llvm-lib  --with-cc clang-14 --with-llvm-config llvm-config-14
RUN make -j$(nproc)
# create lic++ build dir 
WORKDIR /klee_installation_dir/libcpp/
# clone KLEE
WORKDIR /klee_installation_dir/klee/
ADD https://github.com/klee/klee.git ./
# build dir
RUN LLVM_VERSION=14 BASE=/klee_installation_dir/libcpp ENABLE_OPTIMIZED=1 DISABLE_ASSERTIONS=1 ENABLE_DEBUG=0 REQUIRES_RTTI=1 scripts/build/build.sh libcxx
# create build dir
WORKDIR /klee_installation_dir/klee/build
# configure KLEE
RUN cmake -DENABLE_SOLVER_STP=OFF -DENABLE_POSIX_RUNTIME=ON -DENABLE_KLEE_UCLIBC=ON -DKLEE_UCLIBC_PATH=/klee_installation_dir/klee-uclibc/ -DENABLE_KLEE_LIBCXX=ON -DKLEE_LIBCXX_DIR=/klee_installation_dir/libcpp/libc++-install-140/ -DKLEE_LIBCXX_INCLUDE_DIR=/klee_installation_dir/libcpp/libc++-install-140/include/c++/v1/ -DENABLE_KLEE_EH_CXX=ON -DKLEE_LIBCXXABI_SRC_DIR=/klee_installation_dir/libcpp/llvm-140/libcxxabi/ -DENABLE_UNIT_TESTS=ON -DGTEST_SRC_DIR=/klee_installation_dir/googletest-release-1.11.0/ -DLLVM_CONFIG_BINARY=/usr/bin/llvm-config-14 -DLLVMCC=/bin/clang-14 -DLLVMCXX=/bin/clang++-14 /klee_installation_dir/klee/
# MYEDIT: copy the __config_site file
RUN cp /klee_installation_dir/libcpp/libc++-build-140/include/x86_64-unknown-linux-gnu/c++/v1/__config_site /klee_installation_dir/libcpp/libc++-install-140/include/c++/v1/
# build KLEE
RUN make -j$(nproc)
# install
RUN make install
# set required variables for
ENV LLVM_COMPILER="clang"
ENV LLVM_COMPILER_PATH="/lib/llvm-14/bin"
ENV LLVM_CC_NAME="clang-14"

# install auparse
WORKDIR /auparse/
ADD https://github.com/linux-audit/audit-userspace.git ./
RUN apt install -y autoconf automake libtool swig ldap-utils libldap2-dev libwrap0-dev systemd
RUN ./autogen.sh
RUN ./configure --with-python3=yes --enable-gssapi-krb5=yes --with-arm --with-aarch64 --with-libcap-ng=yes --without-golang --with-io_uring
RUN make
RUN make install
# add files to python path
ADD patches/analyze_seccomp_log.py /fuzzypol/seccomp_fuzzing_src/seccomp_analyzer/analyze_seccomp_log.py

# examples
# --------
# originally this was done with a playbook
# RUN ansible-playbook -i inventory install_examples.yml

# run the testsuit
# -----------------
WORKDIR /testsuit/diff
ADD --chmod=700 testsuit/install_diff.sh ./
RUN ./install_diff.sh

WORKDIR /testsuit/tar
ADD --chmod=700 testsuit/install_tar.sh ./
RUN ./install_tar.sh

WORKDIR /testsuit/ls
ADD --chmod=700 testsuit/install_ls.sh ./
RUN ./install_ls.sh

WORKDIR /testsuit/find
ADD --chmod=700 testsuit/install_find.sh ./
RUN ./install_find.sh

# run tests
WORKDIR /testsuit/
ADD --chmod=700 testsuit/run_suit.sh ./
ADD --chmod=700 ./*.sh ./
