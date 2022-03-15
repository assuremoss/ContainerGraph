"""
SecComp 

------------------------------------------------

The default SecComp profile used by Docker:
--security-opt seccomp=docker-default

To load a custom SecComp profile:
docker run ... --security-opt seccomp=my_profile

To do not use any SecComp profile:
--security-opt seccomp=unconfined

------------------------------------------------

"defaultAction": "SCMP_ACT_ERRNO",

"defaultErrnoRet": 1,

"archMap" --> Irrelevant ???

Define a list of syscalls:
"syscalls": [
        {
            "names": "syscall_name",
            "action": "seccomp_action",
            "args": [],
            "includes": {
                "arches": "",
                "caps": "capability_name",
                "...": "..."
            }
            "excludes": {}
        }
]

List of valid SecComp Actions:
https://man7.org/linux/man-pages/man3/seccomp_rule_add.3.html
 - SCMP_ACT_KILL
 - SCMP_ACT_KILL_PROCESS
 - SCMP_ACT_TRAP
 - SCMP_ACT_ERRNO (use to forbit the syscall)
 - SCMP_ACT_TRACE
 - SCMP_ACT_LOG (use to audit)
 - SCMP_ACT_ALLOW (use to allow the syscall)
 - SCMP_ACT_NOTIFY



"""


class SecComp_Profile : 

    def __init__(self, name):
        self.name = name
        # .... MORE TO COME


"""

The parser's output:

 - List of ALLOWED system calls
 - List of DENIED system calls
 - List of GRANTED capabilities

"""





