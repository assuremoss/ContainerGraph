
# Container Security

The following document provides ...


## Linux Capabilities

What are ...


## Linux System Calls

System calls provide an interface to the services made available by the kernel of an operating system. In Linux, a system call is the fundamental interface between an application and the Linux kernel. System calls are generally not invoked directly, but rather via wrapper functions in `glibc` (thus making a system calls looks the same as invoking a normal library function). Often the glibc wrapper function is quite thin, doing little work other than copying arguments to the right registers before invoking the system call, and then setting `errno` appropriately after the system call has returned.

In other words, a system call is an entry point into the Linux kernel. On error, most system calls return a negative error number (e.g. `-1`). The value returned by a successful system call depends on the call, but usually is `0`.

System calls are divided into 5 categories mainly :

 - Process Control (fork, exit, exec)
 - File Management (open, read, write, close)
 - Device Management (ioctl)
 - Information Maintenance (getpid, alarm, sleep)
 - Communication (pipe, shmget, mmap)


https://www.usenix.org/system/files/raid20-ghavamnia.pdf
https://ieeexplore.ieee.org/document/
https://ieeexplore.ieee.org/document/7987222
https://dl.acm.org/doi/pdf/10.1145/3429885.3429966
https://link-springer-com.vu-nl.idm.oclc.org/content/pdf/10.1007/s10664-019-09737-2.pdf
https://mastermjr.com/papers/Towards_Improving_Container_Security_by_Preventing_Runtime_Escapes.pdf
https://github.com/kinvolk/inspektor-gadget
https://man7.org/linux/man-pages/man1/strace.1.html
https://en.wikipedia.org/wiki/Hypervisor
https://github.com/aquasecurity/tracee
https://aquasecurity.github.io/tracee/v0.6.4/
https://cloudblogs.microsoft.com/opensource/2021/11/29/progress-on-making-ebpf-work-on-windows/


https://www.youtube.com/results?search_query=seccomp+container
https://www.youtube.com/watch?v=qxmhfY05oWY
https://www.youtube.com/watch?v=lhToWeuWWfw
https://www.youtube.com/watch?v=tcwmAAJATkc
https://www.youtube.com/watch?v=pVWvjt1KOi0



#### glibc

`glibc` is an acronymn of the standard C library, which is a library of standard functions that can be used by all C programs.


#### errno

The `<errno.h` header file defines the integer variable **errno**, which is set by system calls in the event of an error to indicate what went wrong. The value in errno is significant only when the return value of the call indicate an error. On Linux, you can obtain a list of all symbolic error names by running the following:
```bash
errno -l
```



## Secure Computing Mode (Seccomp)

Seccomp allows restricting system calls that a process inside a container can execute, to a subset of allowed calls.


### Related work on generating (Seccomp) system calls profiles for workloads (e.g. container and pods)




## AppArmor

https://docs.docker.com/engine/security/apparmor/#understand-the-policies
https://gitlab.com/apparmor/apparmor/-/wikis/QuickProfileLanguage
https://gitlab.com/apparmor/apparmor/-/wikis/AppArmor_Core_Policy_Reference#AppArmor_globbing_syntax
https://forums.grsecurity.net/viewtopic.php?t=2522
https://jpetazzo.github.io/2021/11/30/docker-build-container-images-antipatterns/



## SELinux