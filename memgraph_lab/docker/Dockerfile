## Custom Dockerfile
FROM ghcr.io/consol/docker-headless-vnc-container/debian-xfce-vnc:v2.0.1

# Switch to root user to install additional software
USER 0

# Install Required tools
RUN apt update
RUN apt install -y curl \
                   net-tools

# Fetch memgraphlab deb file
RUN curl https://download.memgraph.com/memgraph-lab/v2.4.0/MemgraphLab-2.4.0.deb -o memlab.deb  

# Install memgraphlab
RUN apt install -y ./memlab.deb

# Memgraph lab desktop shortcut
ADD memgraph_lab/docker/memgraph-desktop-shortcut.desktop /headless/Desktop/memgraph-lab.desktop

# Add execute permission to shortcut
RUN chmod +x /headless/Desktop/memgraph-lab.desktop

# switch back to default user
USER 1000

ENTRYPOINT ["/dockerstartup/vnc_startup.sh"]
CMD ["--wait"]