# BabelBrain v0.8.8 (same as the Mac app) on Linux with CUDA 13, for the university GPGPU server 2 (H100, driver 595)
FROM mambaorg/micromamba:2.0.5
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
      git ca-certificates libgl1 libegl1 libxkbcommon0 libfontconfig1 libdbus-1-3 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*
COPY env_trim.yml /tmp/env.yml
RUN micromamba create -y -n babelbrain -f /tmp/env.yml && micromamba clean -a -y
RUN git clone --depth 1 --branch v0.8.8 --recurse-submodules --shallow-submodules \
      https://github.com/ProteusMRIgHIFU/BabelBrain.git /opt/BabelBrain
ENV PATH=/opt/conda/envs/babelbrain/bin:$PATH \
    QT_QPA_PLATFORM=offscreen \
    MPLBACKEND=Agg
WORKDIR /opt/BabelBrain/BabelBrain
