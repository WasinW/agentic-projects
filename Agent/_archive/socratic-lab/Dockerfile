# Socratic (kevins981/Socratic) in a Linux container.
# Socratic requires Linux kernel >= 5.15 and drives the OpenAI Codex CLI as its
# synthesis "brain" — neither runs natively on Intel macOS, so we containerize.
FROM node:20-bookworm-slim

# Debian bookworm ships Python 3.11 (satisfies Socratic's >=3.10). git to clone.
RUN apt-get update && apt-get install -y --no-install-recommends \
        python3 python3-pip git ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# The engine Socratic shells out to (`codex --cd ... --sandbox ...`).
RUN npm install -g @openai/codex

# Clone + install Socratic. Pin nothing here — this is a lab; rebuild to update.
WORKDIR /opt
RUN git clone --depth 1 https://github.com/kevins981/Socratic.git
WORKDIR /opt/Socratic
RUN pip install --break-system-packages -e .

# Web UI (the inspect/diff/approve surface). Optional at runtime.
RUN cd web && npm install --no-audit --no-fund

ENV PYTHONUNBUFFERED=1
WORKDIR /opt/Socratic
CMD ["bash"]
