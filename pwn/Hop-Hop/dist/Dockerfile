FROM ubuntu:24.04

RUN apt-get update -y \
 && apt-get install -y --no-install-recommends socat\
 && rm -rf /var/lib/apt/lists/*

RUN useradd -m ctf

COPY challenge/chall    /home/ctf/chall
COPY challenge/flag.txt /home/ctf/flag.txt

RUN chown -R root:ctf /home/ctf && \
    chmod 750 /home/ctf/chall && \
    chmod 640 /home/ctf/flag.txt

WORKDIR /home/ctf

EXPOSE 10003

CMD ["socat", "TCP-LISTEN:10003,reuseaddr,fork", "EXEC:/home/ctf/chall,stderr"]