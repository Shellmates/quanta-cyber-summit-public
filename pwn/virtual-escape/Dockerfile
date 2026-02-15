FROM ubuntu:22.04

RUN apt-get update && \
    apt-get install -y gcc make netcat socat && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN useradd -m -s /bin/bash ctf

WORKDIR /home/ctf
COPY src/ ./src/
COPY Makefile .
COPY flag.txt .

RUN make DIFFICULTY=MEDIUM && \
    chmod +x vm && \
    chown root:root vm && \
    chmod 755 vm

RUN chown root:root flag.txt && chmod 444 flag.txt

# Create wrapper script for handling network requests
RUN echo '#!/bin/bash' > /home/ctf/handler.sh && \
    echo 'cat > /tmp/bytecode.bin' >> /home/ctf/handler.sh && \
    echo './vm /tmp/bytecode.bin' >> /home/ctf/handler.sh && \
    chmod +x /home/ctf/handler.sh

USER ctf
EXPOSE 9999

CMD socat TCP-LISTEN:9999,reuseaddr,fork EXEC:/home/ctf/handler.sh
