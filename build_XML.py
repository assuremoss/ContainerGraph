from bs4 import BeautifulSoup


def cont_XML_chart(cont, img_id) :
    """
    TODO
    """

    ### Config.###

    ### Permissions ###

    print("TODO")




# Write data to the XML Manifest
def image_XML_chart(img, infra) :
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
        
        ### Infrastructure ###
        bs_data.find('hostname')['name'] = infra.host.hostname
        bs_data.find('os')['type'] = infra.host.os
        bs_data.find('os')['architecture'] = infra.host.architecture
        bs_data.find('kernel')['version'] = infra.host.kernel_v
        bs_data.find('cpus')['number'] = infra.host.cpus
        bs_data.find('mem')['total'] = infra.host.mem

        # TODO
        # Check which container engine is being used and consequently add the tags
        bs_data.find('docker')['version'] = infra.docker_v
        bs_data.find('containerd')['version'] = infra.containerd_v
        bs_data.find('runc')['version'] = infra.runc_v
        bs_data.find('storage')['value'] = infra.storage
        bs_data.find('registry')['value'] = infra.registry

        ### Image ###
        bs_data.find('image')['img_id'] = img.img_id
        bs_data.find('repo')['name'] = img.repo
        bs_data.find('tag')['name'] = img.tag
        bs_data.find('t_created', {'object': 'image'})['value'] = img.t_created
        bs_data.find('size', {'object': 'image'})['value'] = img.img_size
        
        # bs_data.find('Dockerfile')['base_image'] = img.Dockerfile.FROM

        # Save changes to the new container chart
        with open('charts/' + img.img_id + '_chart.xml', 'w') as file:
            file.write(str(bs_data.prettify()))
    
    except OSError:
        print("Error while opening/reading charts/" + img.img_id + "_chart.xml! Exiting...")
        exit(1)

    