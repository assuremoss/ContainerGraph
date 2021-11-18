
# File to automatically generate a Generalized Security Manifest based on the container's configuration

# CHECK ANDROID MANIFEST

# XML style


https://stackoverflow.com/questions/63502218/replacing-placeholders-in-a-text-file-with-python



"""

Generalized Security Manifest

must contain:
 - image
 - infrastructure ??? NOT SURE
 - container
 - network
 - application ??? NOT SURE

can contain:
 - registry
 - host
 - orchestration



Example:

<security_manifest>

    <image> @@image@@ </image>
        <registry> @@registry@@ </registry>
    
    <infrastructure> 
        <host> @@os-release@@ </host>
            <engine> @@container_engine@@ </engine>
    </infrastructure>

    <container> 
        <user>
        <env>
        <volumes>
        <processes>
        < ... >
    </container>

    <network> 
        <ports>
        <protocols>
        <ns> 
        < ... >
    </network>

    <application> 
        <name> ...
        < ... >
    </application>

    ???

</security_manifest>

"""