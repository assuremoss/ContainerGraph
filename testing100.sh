#!/bin/bash

export TOTAL_RUNS=5

export LOG_FILE=execution_times100.log

###

printf "Starting...\n"

# Creating the log file
touch $LOG_FILE 

echo "Execution Times --- ContainerGraph Tool" > $LOG_FILE
echo $(date) >> $LOG_FILE
echo "" >> $LOG_FILE
echo "------------" >> $LOG_FILE
echo "" >> $LOG_FILE


##################################################################################
# TESTING_SCALE = 10

echo "Testing 10 mixed containers "

echo "Cleaning up the database..."
# 1. Clean-up database and remove all containers
python main.py --remove all

# 2. Initialize the database (configuration + vulnerabilities)
echo "Initializing the database..."
python main.py --run ciao >/dev/null

echo "Execution Times for 10 mixed containers" >> $LOG_FILE
echo "" >> $LOG_FILE

echo "Computing Loading and Analyzing times for 10 containers..."

# Loading the Nginx AppArmor profile
# sudo apparmor_parser -r -W ./files/Apparmor/docker-nginx

for i in $(seq 1 $TOTAL_RUNS); do 
    for i in $(seq 1 $TOTAL_RUNS); do 

        echo " > Iteration $i"

        # 1. Container mixed 1 uses 3 of the most common CAPs that we found on GitHub and StackOverflow
        # 2. Container mixed 2 uses other 3 of the most common CAPs that we found on GitHub and StackOverflow
        # 3. Container mixed 3 uses a configuration vulnerable to a container escaping attack
            # https://blog.trailofbits.com/2019/07/19/understanding-docker-container-escapes/
        # 4. Container mixed 4 uses the AppAmor Nginx profile available in the official Docker documentation
            # https://docs.docker.com/engine/security/apparmor/
        # 5. Container mixed 5 uses 3 common recommendations suggested by the Docker CIS Benchmark (i.e., limited cpus and memory)

        # 3. Computing Loading Time
        echo " > $i Loading Time" >> $LOG_FILE
        /usr/bin/time -a -o $LOG_FILE -p sh -c '
        for i in $(seq 1 2); do 
            python main.py --run docker run -it --rm -d --cap-add NET_ADMIN --cap-add SYS_PTRACE nginx >/dev/null;
            python main.py --run docker run -it --rm -d --cap-add CAP_IPC_LOCK --cap-add SYS_ADMIN nginx >/dev/null;
            python main.py --run docker run -it --rm -d --security-opt apparmor=unconfined --cap-add SYS_ADMIN nginx >/dev/null;
            python main.py --run docker run --security-opt apparmor=docker-nginx --security-opt no-new-privileges -d nginx >/dev/null;
            python main.py --run docker run -it --rm -d --cpus=2 -m 1GB nginx >/dev/null;
        done
        '

        # 4. Compute Analyzing Time
        echo " > $i Analyzing Time" >> $LOG_FILE
        yes 2>/dev/null | /usr/bin/time -a -o $LOG_FILE -p python main.py --analyze >/dev/null

        # 5. Clean-up
        python main.py --remove containers >/dev/null
        echo "" >> $LOG_FILE

    done

    python main.py --remove all

done

echo "------------" >> $LOG_FILE
echo "" >> $LOG_FILE

##################################################################################

##################################################################################
# TESTING_SCALE = 100

echo "Testing 100 mixed containers "

echo "Cleaning up the database..."
# 1. Clean-up database and remove all containers
python main.py --remove all

# 2. Initialize the database (configuration + vulnerabilities)
echo "Initializing the database..."
python main.py --run ciao >/dev/null

echo "Execution Times for 100 mixed containers" >> $LOG_FILE
echo "" >> $LOG_FILE

echo "Computing Loading and Analyzing times for 100 containers..."

# Loading the Nginx AppArmor profile
# sudo apparmor_parser -r -W ./files/Apparmor/docker-nginx

for i in $(seq 1 $TOTAL_RUNS); do 
    for i in $(seq 1 $TOTAL_RUNS); do 

        echo " > Iteration $i"

        # 1. Container mixed 1 uses 3 of the most common CAPs that we found on GitHub and StackOverflow
        # 2. Container mixed 2 uses other 3 of the most common CAPs that we found on GitHub and StackOverflow
        # 3. Container mixed 3 uses a configuration vulnerable to a container escaping attack
            # https://blog.trailofbits.com/2019/07/19/understanding-docker-container-escapes/
        # 4. Container mixed 4 uses the AppAmor Nginx profile available in the official Docker documentation
            # https://docs.docker.com/engine/security/apparmor/
        # 5. Container mixed 5 uses 3 common recommendations suggested by the Docker CIS Benchmark (i.e., limited cpus and memory)

        # 3. Computing Loading Time
        echo " > $i Loading Time" >> $LOG_FILE
        /usr/bin/time -a -o $LOG_FILE -p sh -c '
        for i in $(seq 1 20); do 
            python main.py --run docker run -it --rm -d --cap-add NET_ADMIN --cap-add SYS_PTRACE nginx >/dev/null;
            python main.py --run docker run -it --rm -d --cap-add CAP_IPC_LOCK --cap-add SYS_ADMIN nginx >/dev/null;
            python main.py --run docker run -it --rm -d --security-opt apparmor=unconfined --cap-add SYS_ADMIN nginx >/dev/null;
            python main.py --run docker run --security-opt apparmor=docker-nginx --security-opt no-new-privileges -d nginx >/dev/null;
            python main.py --run docker run -it --rm -d --cpus=2 -m 1GB nginx >/dev/null;
        done
        '

        # 4. Compute Analyzing Time
        echo " > $i Analyzing Time" >> $LOG_FILE
        yes 2>/dev/null | /usr/bin/time -a -o $LOG_FILE -p python main.py --analyze >/dev/null

        # 5. Clean-up
        python main.py --remove containers >/dev/null
        echo "" >> $LOG_FILE

    done

    python main.py --remove all

done

echo "------------" >> $LOG_FILE
echo "" >> $LOG_FILE

##################################################################################
