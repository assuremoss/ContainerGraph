from bs4 import BeautifulSoup



# Write data to the XML Manifest
def generate_XML_chart(cont, infra) :
    """ 
    Description

    Parameters
    ---------
    name: type
        Description

    Returns
    -------
    type:
        Description
    """

    try:
        # Open the security template chart
        with open('charts/template_chart.xml', 'r') as file :
            chart = file.read()

        bs_data = BeautifulSoup(chart, "xml")
        
        # Find the first instance of the tag 'hostname'
        b_unique = bs_data.find('hostname')
        print(b_unique)
        
        # Using find() to extract attributes
        # of the first instance of the tag
        b_name = bs_data.find('hostname', {'booh':'booh'})
        print(b_name)
        # Extract value from a tag
        value = b_name.get('booh')
        print(value)

        # Write data to the XML file
        # This is a tag property
        b_unique['booh'] = 'zzz'

        # Change text between XML tags
        bs_data.infrastructure.hostname.string = 'ciaooo'

        # Print changes
        print(b_unique)


        # Save changes to the new container chart
        # with open('charts/' + cont.id + '_chart.xml', 'w') as file:
        #     file.write(chart)
    
    except OSError:
        #print("Error while opening/reading charts/" + cont.id + "_chart.xml! Exiting...")
        exit(1)

    
generate_XML_chart("ciao", "ciao")