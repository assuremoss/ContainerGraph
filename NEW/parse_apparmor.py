"""
AppArmor

------------------------------------------------

The default AppArmor profile used by Docker:
--security-opt apparmor=docker-default

To load a custom profile:
apparmor_parser -r -W /path/to/my_profile
--security-opt apparmor=my_profile

To do not use any AppArmor profile:
--security-opt apparmor=unconfined

------------------------------------------------

 - The order of rules does not matter.

 - Important: deny rules are evaluated before allow rules and cannot be overridden by an allow rule.

------------------------------------------------

The name of the profile is the one after the "profile" keyword:
    profile profile_name flags=... {}

It can also start like this:
    /bin/cat --> will create a profile for cat!
    /usr/bin/firefox {}
    /usr/bin/firefox flags=... {}
    /path/to/executable

Ignore comments --> lines that start with # (do not ignore #include !)

------------------------------------------------

AppArmor Flags

flags=(complain) --> The application will only be constrained by DAC while AppArmor will allow all actions and log any policy violations.

For each rule, you may have empty (allow), deny, and owner.


------------------------------------------------

Capability rules --> grant capabilities

Capability rules do not grant extra capability privileges to a task, but serve to mask the tasks, effective and permitted capability sets. 

 [('audit'|'quiet')' '] [('deny'|'kill'|'nokill')' '] 'capability' <cap> [<extended cap>|(' '<cap>)+] ','

    capability setuid,
    capability setgid,

------------------------------------------------

Network Rules --> AppArmor network rules provide a flexible profile centric approach to creating a firewall. The network rules are flexible in that they provide both control over creation of sockets, flow of data (packets), and can stand alone or be integrated with the system firewall.

    network,           # allow all networking
    deny network,      # disallow all networking
    network inet tcp,  # allow TCP protocol for IPv4 only

Permissions:
    create
    accept
    bind
    connect
    listen
    read
    write
    send
    receive
    getsockname
    getpeername
    getsockopt
    setsockopt
    fcntl
    ioctl
    shutdown
    getpeersec


    network inet, # grant the all permissions set
    deny network bind inet, # subtract bind from inet
    network inet stream,  # allow inet stream == tcp
    network inet raw,
    network tcp,


------------------------------------------------

File Rules --> control how iles are accessed and only occur within a profile. They consist of a pathname, a permission set and are terminated by a comma.

    /path/to/file rw, (we consider only this syntax - convention)

List of permissions:
    r - read
    w - write
    a - append
    l - link 
    k - lock
    m - memory
    x - executable
    

------------------------------------------------

Mount rule

    mount, # allow any mount
    mount options=ro /dev/foo, # mount /dev/foo as read-only    

Options:
    ro, r, read-only   |   rw, w
    suid               |   nosuid
    exec               |   noexec



------------------------------------------------

File Permissions
    r - read
    w - write
    a - append (implied by w)
    x - execute (for now we only consider x)
    m - memory map executable
    k - lock (requires r or w)
    l - link 

------------------------------------------------

Rule Modifiers --> When there is no corresponding rule for a resource, AppArmor will block access to the resource and log it. When there is a rule in the policy, access is allowed to the resource without logging.
The following modifiers can be prepended to a rule to change this behavior:
    audit: force logging
    deny: explicitly denying, without logging
    audit deny

    /path/to/file1          w,  # allow write
    deny /path/to/file2,    w,
    audit /.../.../         w,
    audit deny /.../...     w,




"""



class AppArmor_Profile : 

    def __init__(self, name):
        self.name = name
        # .... MORE TO COME


"""
The parser's output:

 - List of ALLOWED system calls
 - List of DENIED system calls
 - List of GRANTED capabilities
 
 - Network Access ?
 - File Access ?

"""




def retrieve_profile() :
    """
    Given the location of the AppArmor profile, retrieve the file to parse.

    """

    # Ubuntu


    # Mac-OS
    
    print("TODO")


def parse_profile() :
    """
    
    """

    # 1. Get profile name

    # 2. Line starting with #
    #     - ignore comments
    #     - #include ?

    # 3. Capability rules



    # 4. rlimit rules


    # 5. file rules



    # 6. network rules



    # 7. ipc rules


    # 8. Children profiles and hats ^ ?




    print("TODO")





def AppArmor_Parser() :
    """
    Retrieve and parse an AppArmor profile. It will return a list of ...
    """

    # Retrieve the profile file by location
    profile_loc = retrieve_profile()



























