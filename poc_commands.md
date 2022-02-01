
# Proof of Concept

List of commands to perform a simple proof of concept showing the usage of the tool.

```bash

python main.py --help

docker images

python main.py --add ea335eea17ab

python main.py --add 14119a10abf4

python main.py --add 6b44462daa5e

python main.py --list

XML CHART -- open and show

NEO4J QUERY VIEW CHART
 - show fields (e.g. cmd, entrypoint, env)
 - show permissions

python main.py --can-i ea335eea17ab

docker ps

python main.py --run -d --env mysecret='MY_SECRET' --mount source=my-vol,target=$HOME --privileged ea335eea17ab

```

Now we can update the charts and get the first snapshot of the container. Next eBPF...


# Queries example

Does the container have a specific permission?

```bash
MATCH (c:Container:Docker {name: 'ea335eea17ab'})-[:CAN]->(p:Permissions:DefaultP)
WHERE 'chmod' IN p.adminop
RETURN COUNT(c) > 0 
```

Equivalent queries work also with properties that are not of type list, for example 'net_adapt_type':
```bash
MATCH (c:Container:Docker {name: 'ea335eea17ab'})-[:HAS]->(f:ContainerFields)
WHERE 'bridge' IN f.net_adapt_type
RETURN COUNT(c) > 0 
```




Alternative query with the Permission's field as a single node:
```bash
MATCH (c:Container:Docker {name: 'ea335eea17ab'})-[:CAN]->(p:Permissions:DefaultP)-[:HAS]->(Permission:AdminOp:chmod)
RETURN COUNT(c) > 0 
```


# Useful commands

Return everything:
```bash
MATCH p = (a)-[r]->(b)
RETURN *
```

Return all relationships of a container:
```bash
MATCH (c:Container:Docker {name: 'ea335eea17ab'})-[r]->(b)
RETURN r, c, b
```

To remove everything:

```bash
python main.py --remove-all
```


# Interesting Tools

 - runlike https://github.com/lavie/runlike/
   Given an existing docker container, prints the command line necessary to run a copy of it. 

   