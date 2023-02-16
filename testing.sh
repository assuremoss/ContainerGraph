#!/bin/bash
 
: '

Bash script to execute the ContainerGraph tool on several ($TESTING_SCALE) containers, for $TOTAL_RUNS times, saving the execution times (using the time command) of loading N container configurations into the database, and analyzing N containers, into the $LOG_FILE file.

'

# Scale of the number of containers to test at the same time
export TESTING_SCALE=($(seq 1 10 100))

# Total number of runs to test the tool
# For example, we test 10 containers 25 times, retrieving the min, avg, and max execution times.
export TOTAL_RUNS=25

# Log file to save execution times
export LOG_FILE=execution_times.log

###

printf "Starting...\n"

# Neo4J env variables
export NEO4J_ADDRESS=localhost
export NEO4J_PORT=7687
export NEO4J_USER=neo4j
export NEO4J_PWS=password

# Creating the log file
touch $LOG_FILE 

echo "Execution Times --- ContainerGraph Tool" > $LOG_FILE
echo $(date) >> $LOG_FILE
echo "" >> $LOG_FILE
echo "------------" >> $LOG_FILE
echo "" >> $LOG_FILE

##################################################################################
# TESTING_SCALE = 1

echo "Testing 1 container"

echo "Cleaning up the database..."
# 1. Clean-up database and remove all containers
python main.py --remove all

# 2. Initialize the database (configuration + vulnerabilities)
echo "Initializing the database..."
python main.py --run ciao >/dev/null

echo "Execution Times for 1 privileged Docker container" >> $LOG_FILE
echo "" >> $LOG_FILE

for i in $(seq 1 $TOTAL_RUNS); do 

    # 3. Computing Loading Time
    echo " $i Loading Time" >> $LOG_FILE
    /usr/bin/time -h -a -o $LOG_FILE python main.py --run docker run -it --rm -d --privileged nginx >/dev/null
        
    # 4. Compute Analyzing Time
    echo " $i Analyzing Time" >> $LOG_FILE
    yes | /usr/bin/time -h -a -o $LOG_FILE python main.py --analyze >/dev/null

    # 5. Clean-up
    python main.py --remove containers >/dev/null
    echo "" >> $LOG_FILE

done

echo "------------" >> $LOG_FILE
echo "" >> $LOG_FILE

##################################################################################

##################################################################################
# TESTING_SCALE = 10

echo "Testing 10 containers (1 priv. + 9 default)"

echo "Cleaning up the database..."
# 1. Clean-up database and remove all containers
python main.py --remove all

# 2. Initialize the database (configuration + vulnerabilities)
echo "Initializing the database..."
python main.py --run ciao >/dev/null

echo "Execution Times for 10 containers (1 priv. and 9 default)" >> $LOG_FILE
echo "" >> $LOG_FILE

echo "Computing Loading and Analyzing times for 10 containers..."

for i in $(seq 1 $TOTAL_RUNS); do 

    # 3. Computing Loading Time
    echo " $i Loading Time" >> $LOG_FILE
    /usr/bin/time -h -a -o $LOG_FILE sh -c '
    python main.py --run docker run -it --rm -d --privileged nginx >/dev/null;
    python main.py --run docker run -it --rm -d nginx >/dev/null;
    python main.py --run docker run -it --rm -d nginx >/dev/null;
    python main.py --run docker run -it --rm -d nginx >/dev/null;
    python main.py --run docker run -it --rm -d nginx >/dev/null;
    python main.py --run docker run -it --rm -d nginx >/dev/null;
    python main.py --run docker run -it --rm -d nginx >/dev/null;
    python main.py --run docker run -it --rm -d nginx >/dev/null;
    python main.py --run docker run -it --rm -d nginx >/dev/null;
    python main.py --run docker run -it --rm -d nginx >/dev/null;
    '

    # 4. Compute Analyzing Time
    echo " $i Analyzing Time" >> $LOG_FILE
    yes | /usr/bin/time -h -a -o $LOG_FILE python main.py --analyze >/dev/null

    # 5. Clean-up
    python main.py --remove containers >/dev/null
    echo "" >> $LOG_FILE

done

echo "------------" >> $LOG_FILE
echo "" >> $LOG_FILE

##################################################################################

##################################################################################
# TESTING_SCALE = 10

echo "Testing 10 mixed containers "

echo "Cleaning up the database..."
# 1. Clean-up database and remove all containers
python main.py --remove all

# 2. Initialize the database (configuration + vulnerabilities)
echo "Initializing the database..."
python main.py --run ciao >/dev/null

echo "Execution Times for 10 containers (1 priv. and 9 default)" >> $LOG_FILE
echo "" >> $LOG_FILE

echo "Computing Loading and Analyzing times for 10 containers..."

# Loading the Nginx AppArmor profile
apparmor_parser -r -W ./files/Apparmor/docker-nginx

# Create an user to run the container as non-root


for i in $(seq 1 $TOTAL_RUNS); do 

    # 1. Container mixed 1 uses 3 of the most common CAPs that we found on GitHub and StackOverflow
    # 2. Container mixed 2 uses other 3 of the most common CAPs that we found on GitHub and StackOverflow
    # 3. Container mixed 3 uses a configuration vulnerable to a container escaping attack
        # https://blog.trailofbits.com/2019/07/19/understanding-docker-container-escapes/
    # 4. Container mixed 4 uses the AppAmor Nginx profile available in the official Docker documentation
        # https://docs.docker.com/engine/security/apparmor/
    # 5. Container mixed 5 uses 3 common recommendations suggested by the Docker CIS Benchmark (i.e., limited cpus, memory, and not-root user)

    # 3. Computing Loading Time
    echo " $i Loading Time" >> $LOG_FILE
    /usr/bin/time -h -a -o $LOG_FILE sh -c '
    for i in {1..2}; do
    python main.py --run docker run -it --rm -d --cap-add NET_ADMIN --cap-add SYS_PTRACE nginx >/dev/null;
    python main.py --run docker run -it --rm -d --cap-add CAP_IPC_LOCK --cap-add SYS_ADMIN nginx >/dev/null;
    python main.py --run docker run -it --rm -d --security-opt apparmor=unconfined --cap-add SYS_ADMIN nginx >/dev/null;
    python main.py --run docker run -it --rm -d --security-opt apparmor=docker-nginx --security-opt no-new-privileges nginx >/dev/null;
    python main.py --run docker run -it --rm -d --cpus=2 -m 1GB nginx >/dev/null;
    done
    '
    # python main.py --run docker run -it --rm -d --cpus=2 -m 1GB --user $(id -u):$(id -g) nginx >/dev/null;

    docker ps

    # 4. Compute Analyzing Time
    echo " $i Analyzing Time" >> $LOG_FILE
    yes | /usr/bin/time -h -a -o $LOG_FILE python main.py --analyze >/dev/null

    # 5. Clean-up
    python main.py --remove containers >/dev/null
    echo "" >> $LOG_FILE

done

echo "------------" >> $LOG_FILE
echo "" >> $LOG_FILE

##################################################################################

# Run Neo4J container

##################################################################################
# TESTING_SCALE = 100

echo "Testing 100 containers (10 priv. + 90 default)"



##################################################################################
# TESTING_SCALE = 100

echo "Testing 100 mixed containers "

##################################################################################

