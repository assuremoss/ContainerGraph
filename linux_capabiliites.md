
# Linux Capabilities

Linux manual page: https://man7.org/linux/man-pages/man7/capabilities.7.html

## Brief

Linux Capabilities are a list of functionalities in the Linux kernel granted to processes or executables to perform actions usually reserved for privileged processes.

In order to be able to assign capabilities to threads, we have the idea of ‘capability sets’. There are five sets for processes, two of which can also be applied to files.


***The list of "dangerous" capabilities should be based on container escape attacks.***


## List of Linux Capabilities

 • CAP_CHOWN
    - chown

 • CAP_DAC_OVERRIDE
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


## List of Docker default capabilities

And what happens after you run a container with privileges...