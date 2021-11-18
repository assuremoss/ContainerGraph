
class Container:
    
    def __init__(self, id, name, registry, dockerfile, bundle): 
        self.id = id
        self.name = name
        self.registry = registry
        self.Dockerfile = dockerfile
        self.ImageBundle = bundle
