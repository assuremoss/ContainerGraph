
class Container :
    """
    TODO
    """

    def __init__(self, name, user) :
        self.c_name = name
        self.user = user


def build_config(cont, run_args) :
    """
    TODO
    """

    c_name = cont.name
    user = 'root'

    # parse docker run arguments and check for permissions parameters
    for i in range(len(run_args)) :

        # add linux capability
        if run_args[i] == '--name' :
            c_name = run_args[i+1]

        # TODO


 
    return Container(c_name, user)

    