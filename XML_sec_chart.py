import re

# List of fields in the chart that can contain only one value
single_value_fields = ["name", "img_id", "img_id", "filesystem", "docker_v", "os", "kernel_v", "cpus", "mem", "registry", "start_t", "stop_t"]


# Write data to the XML Manifest
def generate_XML_chart(cont, infra) :
    
    try:
        # Open the security chart
        with open('charts/template_chart.xml', 'r') as file :
            chart = file.read()

        # Image fields
        chart = chart.replace("$name$", cont.name)
        chart = chart.replace("$img_id$", cont.img_id)
        chart = chart.replace("$img_id$", cont.img_id)
        chart = chart.replace("$status$", cont.status)
        chart = chart.replace("$filesystem$", cont.filesystem)

        # Infrastructure fields
        chart = chart.replace("$hostname$", infra.hostname)
        chart = chart.replace("$docker_v$", infra.docker_v)
        chart = chart.replace("$os$", infra.os)
        chart = chart.replace("$kernel_v$", infra.kernel_v)
        chart = chart.replace("$cpus$", str(infra.cpus))
        chart = chart.replace("$mem$", str(infra.mem))
        chart = chart.replace("$registry$", infra.registry)

        # Container Config. fields
        # chart = chart.replace("$base_image$", cont.Dockerfile.FROM)
        chart = chart.replace("$user$", cont.Dockerfile.USER)
        if cont.Dockerfile.ENV == "n/a" : chart = chart.replace("$env$", cont.Dockerfile.ENV)
        else : chart = chart.replace("$env$", ', '.join(cont.Dockerfile.ENV))
        if cont.Dockerfile.VOLUME == "n/a" : chart = chart.replace("$volume$", cont.Dockerfile.VOLUME)
        else : chart = chart.replace("$volume$", ', '.join(cont.Dockerfile.VOLUME))
        # The network adapter will eventually be updated at runtime
        chart = chart.replace("$net_adapt_type$", "bridge")
        if cont.Dockerfile.EXPOSE == "n/a" : chart = chart.replace("$expose$", cont.Dockerfile.EXPOSE)
        else : chart = chart.replace("$expose$", ', '.join(cont.Dockerfile.EXPOSE))
        chart = chart.replace("$entrypoint$", cont.Dockerfile.ENTRYPOINT)
        chart = chart.replace("$cmd$", cont.Dockerfile.CMD)

        # Permissions
        chart = chart.replace("$files$", ', '.join(cont.permissions.files))
        chart = chart.replace("$network$", ', '.join(cont.permissions.network))
        chart = chart.replace("$processes$", ', '.join(cont.permissions.processes))
        chart = chart.replace("$adminop$", ', '.join(cont.permissions.adminop))

        # Save changes to the chart
        with open('charts/' + cont.img_id + '_chart.xml', 'w') as file:
            file.write(chart)
    
    except OSError:
        print("Error while opening/reading charts/" + cont.img_id + "_chart.xml! Exiting...")
        exit(1)


# Check whether the field to update supports multi values (e.g. environmental variables) or a single value (e.g. container ID)
def update_XML_chart(img_id, field, value) :

    if field in single_value_fields : 
        new_XML_chart(img_id, field, value)
    else : 
        append_XML_chart(img_id, field, value)


# Update a single-value field (e.g. container's ID)
def new_XML_chart(img_id, field, value) : 

    try:
        # Open the security chart
        with open('charts/' + img_id + '_chart.xml', 'r') as file :
            chart = file.read()

        # Temporarly store the old value of the field
        old_value = chart [ chart.index("<" + field + ">") + 2 + len(field) : chart.index("</" + field + ">")]
        
        # Replate it with the new value
        chart = chart.replace(old_value, value)
        
        # Save changes to the chart
        with open('charts/' + img_id + '_chart.xml', 'w') as file:
            file.write(chart)

    except OSError:
        print("Error while opening/reading charts/" + img_id + "_chart.xml! Exiting...")
        exit(1)


# Append a value to a multi-value field (e.g. ENV variables)
def append_XML_chart(img_id, field, value) : 

    try:
        # Open the security chart
        with open('charts/' + img_id + '_chart.xml', 'r') as file :
            chart = file.read()

        # Temporarly store the old value of the field
        old_value = chart [ chart.index("<" + field + ">") + 2 + len(field) : chart.index("</" + field + ">")]
        
        # If it is the first value of the field, add it
        if old_value == ("n/a") :
            chart = chart.replace(old_value, value)
        
        # otherwise, append the new value
        elif value not in old_value :
            chart = chart.replace(old_value, old_value + ", " + value)

        # Save changes to the chart
        with open('charts/' + img_id + '_chart.xml', 'w') as file:
            file.write(chart)

    except OSError:
        print("Error while opening/reading charts/" + img_id + "_chart.xml! Exiting...")
        exit(1)

