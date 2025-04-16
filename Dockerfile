FROM ubuntu:latest
# installs development tools
RUN apt-get update && apt-get install -y \
    bc \
    vim \
    build-essential \
    cmake \
    git \
    net-tools \
    curl \
    rsync \
    gdb \
    gcc \
    g++ \
    gfortran \
    python3 \
    python3-pip \
    openssh-server
# installs app tools
RUN curl https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -o \
    /tmp/miniconda.sh && \
    /bin/bash /tmp/miniconda.sh -b -p /opt/miniconda && \
    rm /tmp/miniconda.sh
ENV PATH="/opt/miniconda/bin:${PATH}"
RUN conda update -n base -c defaults conda
RUN conda install -c conda-forge -c omnia \
    packmol \
    foyer \
    rdkit \
    mbuild=0.18.0 \
    moltemplate \
    lammps-interface \
    lammps \
    openmm \
    mdanalysis \
    plumed \
    py-plumed \
    natsort \
    langchain \
    langchain-community \
    langchain-openai \
    python-dotenv \
    nbformat \
    ipython
# SSH hack
RUN echo "root: " | chpasswd
RUN ssh-keygen -A
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed -i 's/#PermitEmptyPasswords no/PermitEmptyPasswords yes/' /etc/ssh/sshd_config
RUN sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config
# adds app files
WORKDIR /app
ADD chatbot /app/chatbot
ADD framework_template /app/framework_template
ADD tutorials /app/tutorials
ADD mosdef_HF_env.yaml /app/mosdef_HF_env.yaml
ADD README.md /app/README.md
ADD LICENSE /app/LICENSE
RUN cd /app/tutorials/4_enhanced_sampler/wham/wham && make clean && make && cd /app
ENV PATH="/app/tutorials/4_enhanced_sampler/wham/wham:$PATH"
CMD /bin/bash
