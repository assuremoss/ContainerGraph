
# Linux Capabilities

Linux manual page: https://man7.org/linux/man-pages/man7/capabilities.7.html

## Brief

Kernel capabilities turn the binary “root/non-root” dichotomy into a fine-grained access control system. Linux Capabilities are a list of functionalities in the Linux kernel granted to processes or executables to perform actions usually reserved for privileged processes.

Capabilities are assigned in sets, called "capability sets", which are the following: the set that is checked by the kernel to allow or disallow calls, whereas the others cnotrol how and what capabilities are added or removed from the effective set.

for threads:
   - "effective"
   - "permitted"
   - "inheritable"
   - "bounding"
   - "ambient"

for files:
   - "effective"
   - "permitted"
   - "inheritable"


When setting capabilities on files, you might do something like this `CAP_DAC_OVERRIDE+ep` where e and p denote, respectively, the effective and permitted sets.


The full list of available Linux capabilities for the active kernel can be displayed using the capsh command:

```bash
capsh --print
```


## Retrieving a container's capabilities

```bash
docker inspect -f '{{.State.Pid}}' <container_id>

getpcaps <pid>
```
The getpcaps tool uses the `capget()` system call to query the available capabilities for a particular thread.

In Docker, to drop all capabilities:
```bash
--cap-drop=all
```

To grant a capability:
```bash
--cap-add=<capability>
```


## List of Linux Capabilities

 • CAP_CHOWN: Make changes to the User ID and Group ID of files.
    - chown

 • CAP_DAC_OVERRIDE: Override DAC (Discretionary Access Control). For example, vto bypass read/write/execute permission checks.
 • CAP_DAC_READ_SEARCH
 • CAP_FOWNER

 • CAP_MAC_ADMIN
 • CAP_MAC_OVERRIDE

 • CAP_NET_ADMIN
    - network operations such as interface configuration, IP firewall, modify
      routing tables, ..
 • CAP_NET_BIND_SERVICE
 • CP_NET_BROADCAST
 • CAP_NET_RAW

 • CAP_SETFCAP
 • CAP_SETPCAP

 • CAP_SETUID
 • CAP_SYS_ADMIN
    - mount
    - unmount
    - pivot_root
    - sethostname
    - override RLIMIT_NPROC resource limit
    - open files (accept, execve, open, pipe)
    - clone, unshare
    - setns

 • CAP_SYS_CHROOT
    - chroot, setns

 • CAP_SYS_MODULE

 • CAP_SYS_RAWIO

 • CAP_SYS_RESOURCE
    - setrlimit

 • CAP_KILL: Bypass permission checks for sending signals to processes. 




## List of Docker default capabilities

https://github.com/moby/moby/blob/master/oci/caps/defaults.go#L6-L19