
### WE CAN ALSO GET INFORMATION ABOUT THE INFRASTRUCTURE USING DOCKER CLI ###
"""

$ docker info 

$ docker info -f '{{ .OperatingSystem }}'

$ docker info -f '{{ .KernelVersion }}'

$ ...


"""


class Node :

    def __init__(self, hostname, os, memory, cpu, ip, c_eng_v=0):
        self.hostname = hostname
        self.os = os
        self.memory = memory
        self.cpu = cpu
        self.ip = ip
        self.c_eng_v = c_eng_v


class MasterNode :

    def __init__(self, node) :
        self.node = node
        # Kubernetes version
        # Etcd version
        # etc...


# Vagrant
def get_vagrant(uri) :
    
    hostname = ""
    os = ""
    memory = ""
    cpu = ""
    ip = ""

    f = open(uri, "r")
    lines = f.readlines()

    # iterate over file's lines
    for i, line in enumerate(lines):

        if line != "\n" and not line.startswith('#'): 
            field = line.split(None, 1)[0].strip()

            if field == "IMAGE_NAME" :
                os = line[line.find('"')+1:].strip()
                os = os[:-1]

            elif "memory" in field :
                memory = line[line.find('= ')+2 : ]      
           
            elif "cpus" in field :
                cpu = line[line.find('= ')+2 : ]  
            
            elif "hostname" in field :
                hostname = line[line.find('"')+1:].strip()
                hostname = hostname[:-1]
           
            elif "network" in field :
                ip = line[line.find(': "')+3:].strip()
                ip = ip[:-1]

    aux = Node(hostname, os, memory, cpu, ip)
    return aux



# Kubespray
def get_kubespray(uri) :
    print("TODO")

# kind
def get_kind(uri) :
    print("TODO")

# Terraform
def get_terraform(uri) :
    print("TODO")

# Rancher
def get_rancher(uri) :
    print("TODO")


def get_file_uri() :
    uri = input("Enter path to the infrastructure definition file")
    
    # Check if it exists or not
    
    return uri


def get_infrastructure(platform="Vagrant") :

    #uri = get_file_uri()
    uri = "./Resources/Infrastructure/Vagrantfile"
    
    if platform == "Vagrant" :
        isr = get_vagrant(uri)
    
    elif platform == "kubespray" :
        isr = get_kubespray(uri)
    
    elif platform == "kind" :
        isr = get_kind(uri)
    
    elif platform == "Terraform" :
        isr = get_terraform(uri)
    
    elif platform == "Rancher" :
        isr = get_rancher(uri)
    else : 
        print("Platform not supported! Exiting ...")
        exit(1)

    return isr


### EXAMPLE ###
# my_node = get_infrastructure("Vagrant")

# print(my_node.hostname)
# print(my_node.os)
# print(my_node.memory)
# print(my_node.cpu)
# print(my_node.ip)