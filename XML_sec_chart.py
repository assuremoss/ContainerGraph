import re

### ADD PYTHON EXCEPTIONS WHILE DEALING WITH FILES ###

### TEST WHEN A FIELD NAME IS USED AS A VALUE IN ANOTHER FIELD




# List of fields in the chart that can contain only one value
single_value_fields = ["name", "id", "filesystem", "docker_v", "OS", "kernel_v", "CPUs", "Mem", "Registry", "start_t", "stop_t"]


# Write data to the XML Manifest
def generate_XML_chart(cont, infra) :
    
    # Open the security chart
    with open('charts/template_chart.xml', 'r') as file :
        chart = file.read()

    # Replace placeholders

    # Image
    chart = chart.replace("$id$", cont.ID)

    # Infrastructure
    chart = chart.replace("$docker_v$", infra.docker_v)

    # Container Config.
    chart = chart.replace("$user$", cont.Dockerfile.USER)

    # Permissions
    chart = chart.replace("$files$", ', '.join(cont.permissions.files))
    chart = chart.replace("$network$", ', '.join(cont.permissions.network))
    chart = chart.replace("$processes$", ', '.join(cont.permissions.processes))
    chart = chart.replace("$adminop$", ', '.join(cont.permissions.adminop))

    # Save changes to the chart
    with open('charts/' + cont.ID + '_chart.xml', 'w') as file:
        file.write(chart)


# Check whether the field to update supports multi values (e.g. environmental variables) or a single value (e.g. container ID)
def update_XML_chart(cont, field, value) :

    if field in single_value_fields : 
        new_XML_chart(cont, field, value)
    else : 
        append_XML_chart(cont, field, value)


# Update a single-value field (e.g. container's ID)
def new_XML_chart(cont, field, value) : 
    # Open the security chart
    with open('charts/' + cont.ID + '_chart.xml', 'r') as file :
        chart = file.read()

    # Temporarly store the old value of the field
    old_value = chart [ chart.index("<" + field + ">") + 2 + len(field) : chart.index("</" + field + ">")]
    
    # Replate it with the new value
    chart = chart.replace(old_value, value)
    
    # Save changes to the chart
    with open('charts/' + cont.ID + '_chart.xml', 'w') as file:
        file.write(chart)


# Append a value to a multi-value field (e.g. ENV variables)
def append_XML_chart(cont, field, value) : 

    # Open the security chart
    with open('charts/' + cont.ID + '_chart.xml', 'r') as file :
        chart = file.read()

    # Temporarly store the old value of the field
    old_value = chart [ chart.index("<" + field + ">") + 2 + len(field) : chart.index("</" + field + ">")]
    
    # If it is the first value of the field, add it
    if old_value == "$" + field + "$" :
        chart = chart.replace(old_value, value)
    
    # otherwise, append the new value
    elif value not in old_value :
        chart = chart.replace(old_value, old_value + ", " + value)

    # Save changes to the chart
    with open('charts/' + cont.ID + '_chart.xml', 'w') as file:
        file.write(chart)

