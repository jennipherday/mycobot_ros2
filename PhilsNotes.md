# Notes from Preliminary Work

## Need to set on RPi shell

```bash
ros2-init # Sets up the environment for ROS2 (builtin to bashrc, same as the ROS2 Icon.)
export ROS_DOMAIN_ID=1 # Best to be explicit.
```


## Multicast - How ROS Nodes Communicate
Multicast ran into plenty of challenges, especially with dev containers. The best solution I found was a link-local network directly connecting the host machine and the RPi.
To accomplish this, connect the ethernet port of the RPi to the host machine. 
Confirm the interface name of the ethernet port on both machines using the command:

```bash
ip addr
```

If it is for example `eth0` on the RPi and `eno1` on the host machine, you can set up a link-local network by running the following commands.
On the host machine:

```bash
sudo ip addr add 169.254.100.1/16 dev eno1
sudo ip link set eno0 up
```

This adds an IP address to the ethernet port on the host machine and brings it up. The IP address is a link-local address, which means it is only valid on the local network segment. The `/16` subnet mask is standard for link-local addresses, anf the `169.254.x.x` range is reserved for link-local addresses. The `eno1` interface name may be different on your machine, so make sure to check the output of `ip addr` to find the correct name.

The second command brings the ethernet port up, in case it was down.

On the RPi:

```bash
sudo ip addr add 169.254.100.2/16 dev eth0
sudo ip link set eth0 up
sudo ip route add default dev eth0
```

These commands are similar to the above, with a new, unique IP address for the RPi. The final command adds a default route for traffic to the eth0 device. The default route is only necessary for the RPi because it does not have a default route set up, and multicast needs to know where to go.
The host machine should already have a default route set up. `ip route` will show the routing table.


## Use the same version of the repository on both machines

The syntax and paths for the packages will have changed since it was compiled and shipped on the RPi.
You can copy these over from the host machine to the RPi using `rsync` or `scp`. This will also test your network setup (in part).

```bash
# ssh and backup the original source using IP from above
# Username is `er` and password is `Elephant` by default.
ssh er@169.254.100.2
mv ~/colcon_ws/src/mycobot_ros2 ~/original_source_backup
exit
# Copy the source from the host machine to the RPi.
# From inside the dev container:
scp -r $(pwd) er@169.254.100.2:~/colcon_ws/src/
# Now head back into the RPi and build the package (eta 2 min).
ssh er@169.254.100.2
cd ~/colcon_ws
ros2-init
colcon build
```


## Network Sanity Checks

You can check the network connection using some demo nodes. 
On the RPi:

```bash
ros2-init
ros2 run demo_nodes_cpp talker
```

On the dev container:

```bash
ros2-init
ros2 run demo_nodes_cpp listener
```

You should see the listener node receiving messages from the talker node. If you don't, check your network setup and make sure the IP addresses are correct.

### Check the following

- `ip addr` on both machines should show interfaces on the 169.254.100.x network.
- `echo $ROS_DOMAIN_ID` on both machines should be 1.
- `ip route` on the RPi should show a default route to eth0 at the top: `default dev eth0 scope link`
