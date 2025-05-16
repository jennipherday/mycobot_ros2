# Notes from Preliminary Work

## Need to set on RPi shell
- ros2-init
- export ROS_DOMAIN_ID=1

## Multicast - How ROS Nodes Communicate
Multicast ran into plenty of challenges, especially with dev containers. The best solution I found was a link-local network directly connecting the host machine and the RPi.
To accomplish this, connect the ethernet port of the RPi to the host machine. 
Confirm the interface name of the ethernet port on both machines using the command:

```bash
ip addr
```

If it is for example `eth0` on the RPi and `eno0` on the host machine, you can set up a link-local network by running the following commands.
On the host machine:

```bash
sudo ip addr add 169.254.100.1/16 dev eno2
sudo ip link set eno1 up
```

On the RPi:

```bash
sudo ip addr add 169.254.100.2/16 dev eth0
sudo ip link set eth0 up
sudo ip route add default dev eth0
```

Note: The default route is only necessary for the RPi because it does not have a default route set up. The host machine should already have a default route set up.
`ip route` will show the routing table.


