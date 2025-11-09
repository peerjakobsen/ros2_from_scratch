# ROS2 Jazzy Development Environment

A Docker-based ROS2 Jazzy development environment for macOS (Apple Silicon) with full GUI support via VNC/noVNC.

## Features

- ROS2 Jazzy on ARM64 architecture (Apple Silicon compatible)
- Full desktop environment (XFCE) accessible via web browser or VNC client
- Pre-installed tools: RViz2, rqt, Gazebo, Navigation2
- Hot-reload development: local `src/` folder mounted into container
- Demo package with publisher/subscriber example

## Quick Start

### Easy Method: Use the Helper Script

The `ros2.sh` script automatically handles environment setup, building, and sourcing:

```bash
# Run any ROS2 command directly
./ros2.sh "ros2 topic list"
./ros2.sh "ros2 launch demo_package demo_launch.py"

# Or open an interactive shell (recommended)
./ros2.sh
```

The script will:
1. Start the container if needed
2. Build your workspace
3. Source all necessary setup files
4. Drop you into a shell or run your command

### Manual Method

**1. Start the Development Environment**

```bash
docker compose up -d
```

**2. Access the GUI**

**Option A: Web Browser (Recommended)**
- Open your browser to http://localhost:6080
- No VNC client needed!

**Option B: VNC Client**
- Connect to `vnc://localhost:5901`
- Password: `password`

**3. Run ROS2 Commands**

```bash
# Open interactive shell with everything set up
./ros2.sh

# Or run commands directly
./ros2.sh "ros2 launch demo_package demo_launch.py"
```

You should see the talker publishing messages and the listener receiving them.

## Project Structure

```
.
├── docker-compose.yml       # Docker Compose configuration
├── src/                     # Your ROS2 packages (mounted into container)
│   └── demo_package/        # Sample ROS2 package
│       ├── package.xml      # Package metadata
│       ├── setup.py         # Python package setup
│       ├── resource/        # Package resources
│       ├── demo_package/    # Python source code
│       │   ├── talker.py    # Publisher node
│       │   └── listener.py  # Subscriber node
│       └── launch/          # Launch files
│           └── demo_launch.py
└── README.md
```

## Environment Variables

You can customize the behavior by editing `docker-compose.yml`:

- `AUTO_BUILD=1`: Automatically build workspace on container start (default: 1)
- `AUTO_LAUNCH=0`: Automatically launch demo on container start (default: 0)

To enable auto-launch, change `AUTO_LAUNCH=0` to `AUTO_LAUNCH=1` in docker-compose.yml.

## Common Commands

### Inside the Container

```bash
# Source ROS2 (already in ~/.bashrc)
source /opt/ros/jazzy/setup.bash

# Build workspace
cd /root/ros2_ws
colcon build

# Source your workspace
source install/setup.bash

# List available nodes
ros2 node list

# List topics
ros2 topic list

# Echo a topic
ros2 topic echo /chatter

# Run individual nodes
ros2 run demo_package talker
ros2 run demo_package listener

# Launch with launch file
ros2 launch demo_package demo_launch.py

# Open RViz
rviz2

# Open rqt
rqt
```

### On Your Mac

```bash
# Start the environment
docker compose up

# Start in background
docker compose up -d

# View logs
docker compose logs -f

# Stop the environment
docker compose down

# Rebuild after changes to docker-compose.yml
docker compose up --build

# Execute commands in running container
docker compose exec ros2_dev bash
```

## Creating New Packages

### Python Package

```bash
cd /root/ros2_ws/src
ros2 pkg create --build-type ament_python my_package --dependencies rclpy std_msgs
cd /root/ros2_ws
colcon build --packages-select my_package
```

### C++ Package

```bash
cd /root/ros2_ws/src
ros2 pkg create --build-type ament_cmake my_cpp_package --dependencies rclcpp std_msgs
cd /root/ros2_ws
colcon build --packages-select my_cpp_package
```

## Troubleshooting

### Container won't start
- Ensure Docker Desktop is running
- Check that ports 5901 and 6080 are not in use
- Try: `docker compose down` then `docker compose up`

### Can't connect to VNC
- Wait 30 seconds after container start for VNC to initialize
- Check container logs: `docker compose logs`
- Verify the container is running: `docker ps`

### Build fails
- Ensure your package.xml and setup.py are configured correctly
- Check for missing dependencies
- Try cleaning: `rm -rf build install log` then rebuild

### GUI apps won't display
- Ensure DISPLAY=:1 is set (should be automatic)
- Check VNC is running: `ps aux | grep Xvnc`
- Restart the container: `docker compose restart`

## Pre-installed ROS2 Packages

- `ros-jazzy-desktop`: Full desktop install
- `ros-jazzy-rviz2`: 3D visualization
- `ros-jazzy-rqt`: Qt-based GUI tools
- `ros-jazzy-navigation2`: Navigation stack
- `ros-jazzy-gazebo-ros-pkgs`: Gazebo simulator integration

## Tips

1. **Code on macOS, build in Docker**: Edit code in your favorite macOS editor. Changes are immediately reflected in the container since `src/` is mounted.

2. **Multiple terminals**: You can open multiple terminals in the container:
   ```bash
   docker compose exec ros2_dev bash
   ```

3. **GUI in browser**: The web VNC interface (http://localhost:6080) is the easiest way to access GUI tools without installing a VNC client.

4. **Persistent data**: The `src/` folder is on your Mac. Container restarts won't lose your code. However, `build/`, `install/`, and `log/` folders are inside the container and will be rebuilt.

## Next Steps

1. Explore the demo package code in `src/demo_package/`
2. Modify the talker or listener to experiment
3. Create your own ROS2 packages
4. Try running RViz2 or Gazebo from the GUI
5. Explore the Navigation2 stack

## Resources

- [ROS2 Documentation](https://docs.ros.org/en/jazzy/)
- [ROS2 Tutorials](https://docs.ros.org/en/jazzy/Tutorials.html)
- [Navigation2](https://navigation.ros.org/)
- [Gazebo](https://gazebosim.org/)
