FROM docker.io/althack/ros2:galactic-full

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
    && apt-get -y install --no-install-recommends \
    python3-pip \
    python3.8-venv \
    ros-${ROS_DISTRO}-rclpy \
    ros-${ROS_DISTRO}-moveit\
    build-essential \
    python3-colcon-common-extensions \
    libopencv-dev \
    python3-opencv \
    # Clean up
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

ENV DEBIAN_FRONTEND=dialog

# Set up auto-source of workspace for ros user
ARG WORKSPACE
RUN echo "if [ -f ${WORKSPACE}/install/setup.bash ]; then source ${WORKSPACE}/install/setup.bash; fi" >> /home/ros/.bashrc
