docker build -t hop-hop-compile .
docker run --rm -v "$(pwd)/..:/out" hop-hop-compile bash -c "
    cd /out/challenge &&
    gcc -z relro -z now -no-pie -fno-PIE -fno-stack-protector -o chall chall.c -lseccomp
"
sudo chown kali:kali ../challenge/chall
ln -f ../challenge/chall ../dist/chall
cp ../challenge/chall ../solve/chall
patchelf --set-interpreter ./ld-linux-x86-64.so.2 --set-rpath . ../solve/chall