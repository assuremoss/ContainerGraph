from setuptools import setup

with open('requirements.txt', 'r') as r:
    reqs = r.read().split('\n')

setup(
    name='ContainerGraph',
    version='1.0.0',
    author='Francesco Minna',
    email='f.minna@vu.nl',
    description='A tool to generate security charts (in XML and Neo4J) for containers.',
    # packages=['containergraph'],
    install_requires=reqs
)