
class Dockerfile:

    # add : str to fields, EXPOSE: iter
    def __init__(self, FROM, RUN, COPY, CMD, WORKDIR, LABEL, EXPOSE, ENV, ADD, ENTRYPOINT, VOLUME, USER, ARG, ONBUILD, STOPSIGNAL, HEALTHCHECK, SHELL):
        self.FROM = FROM # 1, non-emtpy, FROM <image> AS something (delete everything after <image>)
        self.RUN = RUN 
        self.COPY = COPY 
        self.CMD = CMD 
        self.WORKDIR = WORKDIR  
        self.LABEL = LABEL 
        self.EXPOSE = EXPOSE
        self.ENV = ENV
        self.ADD = ADD
        self.ENTRYPOINT = ENTRYPOINT 
        self.VOLUME = VOLUME
        self.USER = USER 
        self.ARG = ARG
        self.ONBUILD = ONBUILD
        self.STOPSIGNAL = STOPSIGNAL
        self.HEALTHCHECK = HEALTHCHECK
        self.SHELL = SHELL


# Reads a Dockerfile and returns a Dockerfile object
def parse_Dockerfile(uri):

    FROM="n/a"
    RUN="n/a"
    COPY="n/a"
    CMD="n/a" 
    WORKDIR="n/a"
    LABEL="n/a"
    EXPOSE="n/a"
    ENV="n/a"
    ADD="n/a"
    ENTRYPOINT="n/a"
    VOLUME="n/a"
    USER="root"
    ARG="n/a"
    ONBUILD="n/a"
    STOPSIGNAL="n/a"
    HEALTHCHECK="n/a"
    SHELL="n/a"

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

            # Store field and value
            if field == "FROM":
                # Ignore eventual rename (e.g. FROM example AS my_img)
                FROM = value.split()[0]
            elif field == "RUN":
                if RUN == "n/a": RUN = [value]
                else :
                    RUN.append(value)
            elif field == "COPY":
                if COPY == "n/a" : COPY = [value]
                else: COPY.append(value)
            elif field == "CMD":
                CMD = value
            elif field == "WORKDIR":
                WORKDIR = value
            elif field == "LABEL":
                LABEL = value
            elif field == "EXPOSE":
                if EXPOSE == "n/a" : EXPOSE = [value]
                else: EXPOSE.append(value)
            elif field == "ENV":
                if ENV == "n/a" : ENV = [value]
                else: ENV.append(value)
            elif field == "ADD":
                if ADD == "n/a" : ADD = [value]
                else: ADD.append(value)
            elif field == "ENTRYPOINT":
                ENTRYPOINT = value
            elif field == "VOLUME":
                if VOLUME == "n/a" : VOLUME = [value]
                else: VOLUME.append(value)
            elif field == "USER":
                USER = value
            elif field == "ARG":
                if ARG == "n/a": ARG = [value]
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

    # Strip brackets and quotes
    ENTRYPOINT = ENTRYPOINT.strip('["/').strip('"]')
    CMD = CMD.strip('["').strip('"]')
    CMD = CMD.replace('"', '')

    # create a Dockerfile object to return
    aux = Dockerfile(FROM, RUN, COPY, CMD, WORKDIR, LABEL, EXPOSE, ENV, ADD, ENTRYPOINT, VOLUME, USER, ARG, ONBUILD, STOPSIGNAL, HEALTHCHECK, SHELL)
    return aux


def build_Dockerfile():
    
    uri = "Dockerfile"

    rst = parse_Dockerfile(uri)
    return rst

