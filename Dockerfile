FROM ubuntu:24.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV ROS_DISTRO=jazzy
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# Install basic utilities
RUN apt-get update && apt-get install -y \
    curl \
    gnupg2 \
    lsb-release \
    software-properties-common \
    wget \
    git \
    locales \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Setup locale
RUN locale-gen en_US en_US.UTF-8 && \
    update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8

# Enable universe repository
RUN add-apt-repository universe

# Add ROS2 apt repository
RUN curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) main" | tee /etc/apt/sources.list.d/ros2.list > /dev/null

# Install ROS2 Jazzy Desktop and additional packages
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y \
    ros-jazzy-desktop \
    ros-jazzy-navigation2 \
    ros-jazzy-nav2-bringup \
    ros-jazzy-sensor-msgs \
    && rm -rf /var/lib/apt/lists/*

# Install build tools and dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-colcon-common-extensions \
    python3-pip \
    python3-rosdep \
    python3-matplotlib \
    && rm -rf /var/lib/apt/lists/*

# Initialize rosdep
RUN rosdep init && rosdep update

# Install VNC and GUI tools
RUN apt-get update && apt-get install -y \
    tigervnc-standalone-server \
    tigervnc-common \
    xfce4 \
    xfce4-terminal \
    dbus-x11 \
    xfonts-base \
    && rm -rf /var/lib/apt/lists/*

# Install noVNC
RUN git clone --depth 1 https://github.com/novnc/noVNC.git /opt/novnc && \
    git clone --depth 1 https://github.com/novnc/websockify /opt/novnc/utils/websockify && \
    ln -sf /opt/novnc/vnc.html /opt/novnc/index.html

# Setup VNC
RUN mkdir -p /root/.vnc && \
    echo "password" | vncpasswd -f > /root/.vnc/passwd && \
    chmod 600 /root/.vnc/passwd

# Create workspace directory
RUN mkdir -p /root/ros2_ws/src

# Setup ROS2 environment in bashrc
RUN echo "source /opt/ros/jazzy/setup.bash" >> /root/.bashrc

WORKDIR /root/ros2_ws

# Expose VNC and noVNC ports
EXPOSE 5901 6080

CMD ["bash"]
