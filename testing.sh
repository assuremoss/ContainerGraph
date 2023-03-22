#!/bin/bash
 
: '

Bash script to execute the ContainerGraph tool on several ($TESTING_SCALE) containers, for $TOTAL_RUNS times, saving the execution times (using the time command) of loading N container configurations into the database, and analyzing N containers, into the $LOG_FILE file.

'

# Total number of runs to test the tool
# For example, we test 10 containers 25 times, retrieving the min, avg, and max execution times.
export TOTAL_RUNS=4

# Log file to save execution times
export LOG_FILE=execution_times.log

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
# TESTING_SCALE = 500

echo "Testing 500 mixed containers "

echo "Cleaning up the database..."
# Clean-up database and remove all containers
python main.py --remove all >/dev/null

echo "Execution Times for 500 mixed containers" >> $LOG_FILE
echo "" >> $LOG_FILE

echo "Computing Loading and Analyzing times for 500 containers..."

# Loading the Nginx AppArmor profile
# sudo apparmor_parser -r -W ./files/Apparmor/docker-nginx

for i in $(seq 1 $TOTAL_RUNS); do 
    python main.py --run ciao >/dev/null
    for i in $(seq 1 5); do 

        echo " > Iteration $i"

        # 1. Container mixed 1 uses 3 of the most common CAPs that we found on GitHub and StackOverflow
        # 2. Container mixed 2 uses other 3 of the most common CAPs that we found on GitHub and StackOverflow
        # 3. Container mixed 3 uses a configuration vulnerable to a container escaping attack
            # https://blog.trailofbits.com/2019/07/19/understanding-docker-container-escapes/
        # 4. Container mixed 4 uses the AppAmor Nginx profile available in the official Docker documentation
            # https://docs.docker.com/engine/security/apparmor/
        # 5. Container mixed 5 uses 3 common recommendations suggested by the Docker CIS Benchmark (i.e., limited cpus and memory)

        # Computing Loading Time
        echo " > $i Loading Time" >> $LOG_FILE
        /usr/bin/time -a -o $LOG_FILE -p sh -c '
        for i in $(seq 1 50); do 
            python main.py --run docker run -it --rm -d --cap-add NET_ADMIN --cap-add SYS_PTRACE nginx >/dev/null;
            python main.py --run docker run -it --rm -d --cap-add CAP_IPC_LOCK --cap-add SYS_ADMIN nginx >/dev/null;
            python main.py --run docker run -it --rm -d --security-opt apparmor=unconfined --cap-add SYS_ADMIN nginx >/dev/null;
            python main.py --run docker run --security-opt apparmor=docker-nginx --security-opt no-new-privileges -d nginx >/dev/null;
            python main.py --run docker run -it --rm -d --cpus=2 -m 1GB nginx >/dev/null;
            python main.py --run docker run -it --rm -d --privileged nginx >/dev/null;
            python main.py --run docker run -it --rm -d nginx >/dev/null;
            python main.py --run docker run -it --rm -d nginx >/dev/null;
            python main.py --run docker run -it --rm -d nginx >/dev/null;
            python main.py --run docker run -it --rm -d nginx >/dev/null;
        done
        '

        # Compute Analyzing Time
        echo " > $i Analyzing Time" >> $LOG_FILE
        yes 2>/dev/null | /usr/bin/time -a -o $LOG_FILE -p python main.py --analyze >/dev/null

        # Clean-up
        python main.py --remove containers >/dev/null
        echo "" >> $LOG_FILE

    done

    python main.py --remove all >/dev/null

done

echo "------------" >> $LOG_FILE
echo "" >> $LOG_FILE

##################################################################################
