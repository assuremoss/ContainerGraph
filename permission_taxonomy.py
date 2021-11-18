

### PERHAPS THIS CAN BE A JSON FILE, AND NOT A CLASS  !!!

class Permissions : 
    
    def __init__(self, must, internet, files, other):
        self.must = must
        self.internet = internet
        self.files = files
        self.other = other




# List of capabilities without which the container doesn't work
must = ["CAP_1", "CAP_2", "..."]

# List of capabilities related to network management/connection/etc.
# internet CAN also be equal to None, in case there is no connectivity!
internet = [""]

# List of capabilities related to read/write/execute files
files = [""]

# List of other capabilities (admin operations), such as mount, adduser, etc.
other = [""]







def create_Permissions() :
    print("TODO")