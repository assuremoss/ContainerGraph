
### RETRIEVE DOCKERFILES FROM GITHUB ###

# github.com > Search: filename:Dockerfile



class Dockerfile:

    # add : str to fields, EXPOSE: iter
    def __init__(self, FROM, RUN=[], COPY=[], CMD=[], WORKDIR="", LABEL="", EXPOSE=[], ENV=[], ADD=[], ENTRYPOINT="", VOLUME=[], USER="root", ARG=[], ONBUILD="", STOPSIGNAL="", HEALTHCHECK="", SHELL=""):
        self.FROM = FROM # 1, non-emtpy, FROM <image> AS something (delete everything after <image>)
        self.RUN = RUN # non-emtpy
        self.COPY = COPY # non-emtpy
        self.CMD = CMD # 
        self.WORKDIR = WORKDIR # 1, 
        self.LABEL = LABEL # 1
        self.EXPOSE = EXPOSE
        self.ENV = ENV
        self.ADD = ADD
        self.ENTRYPOINT = ENTRYPOINT # 1
        self.VOLUME = VOLUME
        self.USER = USER # 1
        self.ARG = ARG
        self.ONBUILD = ONBUILD
        self.STOPSIGNAL = STOPSIGNAL
        self.HEALTHCHECK = HEALTHCHECK
        self.SHELL = SHELL


# Reads a Dockerfile and returns a Dockerfile object
def parse_Dockerfile(uri):

    FROM=""
    RUN=[]
    COPY=[]
    CMD=[] 
    WORKDIR=""
    LABEL=""
    EXPOSE=[]
    ENV=[]
    ADD=[]
    ENTRYPOINT=""
    VOLUME=[]
    USER="root"
    ARG=[]
    ONBUILD=""
    STOPSIGNAL="" 
    HEALTHCHECK=""
    SHELL=""

    f = open(uri, "r")
    lines = f.readlines()
    
    # iterate over file's lines
    for i, line in enumerate(lines):
        
        if line != "\n" and not line.startswith('#'): # skip empty and comments lines

            # Empty initialization
            field = ""
            value = ""

            # Check if the current command is a multi-line command
            if "\\" in line: 
                
                # If it is the first line of a multi-line command
                if i > 0 and "\\" not in line[i-1] : 

                    field = line.split(None, 1)[0]
                    value = [line[line.find(' ')+1:].replace(" \\\n", "")]
                    
                    for y, itm in enumerate(lines[i+1:]) :
                        value.extend([itm.strip()]) 
                        # if the line does not contains "\", it is the last
                        # line of the command, thus exit
                        if "\\" not in itm : break

            # Single-line command
            else :
                field = line.split(None, 1)[0]
                value = line[line.find(' ')+1:].strip()


            ### CONTAINERS RUNNING AS ROOT ###

            # By default, containers run as root and this should be disable (e.g. creating a new USER).
            # However, running containers as non-root might present challenges where you wish to bind 
            # mount volumes from the underlying host. Thus, we need to check when this latter is the
            # case.

            ### ###


            # store field and value
            if field == "FROM":
                # Ignore eventual rename (e.g. FROM example AS my_img)
                FROM = value.split()[0]
            elif field == "RUN":
                if not RUN: RUN = [value]
                else :
                    RUN.append(value)
            elif field == "COPY":
                if not COPY: COPY = [value]
                else: COPY.append(value)
            elif field == "CMD":
                if not CMD: CMD = [value]
                else: CMD.append(value)
            elif field == "WORKDIR":
                WORKDIR = value
            elif field == "LABEL":
                LABEL = value
            elif field == "EXPOSE":
                # TODO: check for the protocol, e.g. 3000/tcp
                if not EXPOSE: EXPOSE = [value]
                else: EXPOSE.append(value)
            elif field == "ENV":
                if not ENV: ENV = [value]
                else: ENV.append(value)
            elif field == "ADD":
                if not ADD: ADD = [value]
                else: ADD.append(value)
            elif field == "ENTRYPOINT":
                ENTRYPOINT = value
            elif field == "VOLUME":
                if not VOLUME: VOLUME = [value]
                else: VOLUME.append(value)
            elif field == "USER":
                USER = value
            elif field == "ARG":
                if not ARG: ARG = [value]
                else: ARG.append(value)
            elif field == "ONBUILD":
                ONBUILD = value
            elif field == "STOPSIGNAL":
                STOPSIGNAL = value
            elif field == "HEALTHCHECK":
                HEALTHCHECK = value
            elif field == "SHELL":
                SHELL = value

            value = field = ""

    f.close()

    if USER == "":
        USER = "root"

    # create a Dockerfile object to return
    aux = Dockerfile(FROM, RUN , COPY , CMD , WORKDIR , LABEL , EXPOSE , ENV , ADD , ENTRYPOINT , VOLUME , USER, ARG , ONBUILD , STOPSIGNAL , HEALTHCHECK , SHELL)
    return aux


def build_Dockerfile():
    
    uri = "Dockerfile"

    rst = parse_Dockerfile(uri)
    return rst
