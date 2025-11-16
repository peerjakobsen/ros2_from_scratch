# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **ROS2 Jazzy Development Environment** for Apple Silicon (ARM64) with Docker support. It provides containerized Ubuntu environments with:
- ROS2 Jazzy on ARM64 architecture
- Full XFCE desktop GUI accessible via VNC/noVNC web interface
- Pre-installed tools: RViz2, rqt, Navigation2
- **Gazebo Harmonic simulation** in a separate container
- ROS2 bridge network for communication between containers
- Hot-reload development with local `src/` folder mounted into containers

The project contains a Docker Compose setup that runs a complete ROS2 development environment with two containers:
1. **ros2_dev**: Main development environment with ROS2 tools
2. **gazebo**: Gazebo Harmonic simulator with ROS2 integration

Both containers share the same ROS2 domain (ROS_DOMAIN_ID=42) for seamless topic/service communication.

## Quick Commands

### Starting and Accessing the Environment

```bash
# ROS2 Development Container
./ros2.sh                                    # Open interactive ROS2 shell
./ros2.sh "ros2 topic list"                 # Run specific ROS2 commands
./ros2.sh "ros2 launch demo_package demo_launch.py"

# Gazebo Simulation Container
./gazebo.sh                                  # Open interactive Gazebo shell
./gazebo.sh "gz sim"                        # Launch Gazebo simulator
./gazebo.sh "ros2 topic list"               # See ROS2 topics from Gazebo container

# Manual Docker commands
docker compose up -d                         # Start all containers in background
docker compose up -d ros2_dev               # Start only ROS2 dev container
docker compose up -d gazebo                 # Start only Gazebo container
docker compose logs -f gazebo               # View Gazebo container logs
docker compose down                          # Stop all containers
docker compose exec ros2_dev bash           # Execute commands in ROS2 container
docker compose exec gazebo bash             # Execute commands in Gazebo container
```

### Inside the Container (via ./ros2.sh or docker compose exec)

```bash
# Build workspace
cd /root/ros2_ws
colcon build

# Source ROS2 and workspace
source /opt/ros/jazzy/setup.bash
source install/setup.bash

# Common ROS2 commands
ros2 node list                               # List running nodes
ros2 topic list                              # List available topics
ros2 topic echo /chatter                     # Monitor topic messages
ros2 run my_py_pkg test_node                 # Run Python node
ros2 launch demo_package demo_launch.py      # Launch with launch file

# Create new packages
ros2 pkg create --build-type ament_python my_package --dependencies rclpy std_msgs
ros2 pkg create --build-type ament_cmake my_cpp_package --dependencies rclcpp std_msgs
```

### GUI Access

**ROS2 Development Container:**
- **Web VNC (Recommended)**: http://localhost:6080
- **VNC Client**: `vnc://localhost:5901` (password: `password`)
- After connecting, run `rviz2` or `rqt` to access GUI tools

**Gazebo Simulation Container:**
- **Web VNC (Recommended)**: http://localhost:6081
- **VNC Client**: `vnc://localhost:5902` (password: `password`)
- After connecting, run `gz sim` to launch Gazebo

### Gazebo-Specific Commands

```bash
# Inside Gazebo container (via ./gazebo.sh)
gz sim                                       # Launch Gazebo with default world
gz sim /root/gazebo_worlds/empty_world.sdf  # Launch with specific world file
ros2 launch gazebo_ros gazebo.launch.py     # Launch Gazebo via ROS2

# Test ROS2 bridge between containers
# In one terminal (ros2_dev):
./ros2.sh "ros2 topic pub /test std_msgs/msg/String '{data: \"Hello from ROS2\"}'"

# In another terminal (gazebo):
./gazebo.sh "ros2 topic echo /test"         # Should receive the message
```

## Architecture

### Directory Structure

```
ros2_from_scratch/
├── Dockerfile                 # Builds ARM64 Ubuntu image with ROS2 Jazzy (dev container)
├── Dockerfile.gazebo          # Builds ARM64 Ubuntu image with Gazebo Harmonic
├── docker-compose.yml         # Orchestrates both containers with shared network
├── ros2.sh                    # Helper script for ROS2 development container
├── gazebo.sh                  # Helper script for Gazebo simulation container
├── .pylintrc                  # Python linting configuration
├── .vscode/settings.json      # VS Code Python formatter/linter settings
├── ros2_ws/
│   ├── src/                   # ROS2 package source code (mounted in both containers)
│   │   ├── my_py_pkg/         # Example Python package (ament_python)
│   │   └── my_cpp_pkg/        # Example C++ package (ament_cmake)
│   ├── build/                 # Generated build files (container-only)
│   ├── install/               # Installed packages (container-only)
│   └── log/                   # Build logs (container-only)
├── gazebo_worlds/             # Gazebo world files (mounted in Gazebo container)
│   └── empty_world.sdf        # Example empty world
└── pyproject.toml             # Local Python dev tools (pylint, black, isort)
```

### Key Components

#### Docker Container Setup

**ROS2 Development Container (ros2_dev):**
- **Image**: Ubuntu (ARM64) with ROS2 Jazzy Desktop, XFCE, VNC
- **Volume Mounts**:
  - `src/` — mounted as read-write (code changes sync immediately)
  - `build/`, `install/`, `log/` — mounted as read-write
- **Ports**: 5901 (VNC), 6080 (noVNC web)
- **Environment Variables**:
  - `AUTO_BUILD=1` (auto-build on startup)
  - `AUTO_LAUNCH=0` (don't auto-launch)
  - `ROS_DOMAIN_ID=42` (shared domain for multi-container communication)

**Gazebo Simulation Container (gazebo):**
- **Image**: Ubuntu (ARM64) with ROS2 Jazzy Base, Gazebo Harmonic, XFCE, VNC
- **Volume Mounts**:
  - `src/` — mounted as read-only (shares packages from ros2_dev)
  - `gazebo_worlds/` — mounted as read-write (custom world files)
  - `gazebo_models` — Docker volume for Gazebo model cache
- **Ports**: 5902 (VNC), 6081 (noVNC web)
- **Environment Variables**:
  - `ROS_DOMAIN_ID=42` (shared domain for multi-container communication)
  - `GZ_SIM_RESOURCE_PATH=/root/gazebo_worlds` (custom world files path)

**Shared Network:**
- Both containers communicate via a Docker bridge network (`ros2_network`)
- ROS2 topics, services, and actions are shared automatically via DDS
- No manual bridge configuration needed - same ROS_DOMAIN_ID enables discovery

#### ROS2 Packages
- **my_py_pkg**: Python package using `ament_python` build type
  - Entry point: `test_node` command maps to `my_py_pkg.my_first_node:main`
  - Tests use pytest; linting configured in `.pylintrc`
- **my_cpp_pkg**: C++ package using `ament_cmake` build type
  - Uses rclcpp library for C++ ROS2 development

#### Helper Scripts

**ros2.sh** - ROS2 Development Container:
1. Checks if ros2_dev container is running; starts it if needed
2. Runs `colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release`
3. Sources ROS2 and workspace setup files
4. Either opens an interactive shell or runs the provided command

**gazebo.sh** - Gazebo Simulation Container:
1. Checks if gazebo container is running; starts it if needed
2. Sources ROS2 and workspace setup files (if available)
3. Either opens an interactive shell or runs the provided command
4. Provides access to Gazebo GUI at http://localhost:6081

Both scripts eliminate the need to manually source environment files for each command.

## Development Workflow

### Local Code Editing → Container Building

1. **Edit code locally** on macOS using your preferred editor (the `src/` folder is mounted)
2. **Run ./ros2.sh** to automatically:
   - Start the ros2_dev container if needed
   - Build the workspace
   - Open an interactive shell or run a command
3. **Changes in src/ are immediately visible** in both containers due to volume mounting
4. **Build artifacts** (build/, install/, log/) are persisted in the ros2_dev container
5. **Gazebo container** has read-only access to src/ and can use built packages from ros2_dev

### Working with Gazebo Simulations

1. **Start both containers**:
   ```bash
   docker compose up -d
   ```

2. **Build your ROS2 packages** in the dev container:
   ```bash
   ./ros2.sh  # Build and enter shell
   ```

3. **Launch Gazebo** in the simulation container:
   ```bash
   ./gazebo.sh "gz sim /root/gazebo_worlds/empty_world.sdf"
   ```

4. **Test communication** between containers:
   - In ros2_dev: Publish to a topic
   - In gazebo: Subscribe to the same topic
   - Both containers share ROS_DOMAIN_ID=42, so topics/services are automatically bridged

5. **Add custom world files** to `gazebo_worlds/` directory - they'll be available in the Gazebo container

### Creating New ROS2 Packages

**Python Package:**
```bash
./ros2.sh "ros2 pkg create --build-type ament_python my_new_package --dependencies rclpy std_msgs"
```

**C++ Package:**
```bash
./ros2.sh "ros2 pkg create --build-type ament_cmake my_cpp_package --dependencies rclcpp std_msgs"
```

After creating a package, update the entry points in `setup.py` (Python) or `CMakeLists.txt` (C++) to register your node executables.

## Code Style and Linting

### Python Code Style
- **Line Length**: 120 characters (configured in `.pylintrc`)
- **Linting**: Configured via `.pylintrc` with:
  - Some checks disabled: `missing-docstring`, `too-many-arguments`, `import-error`, etc.
  - ROS2 modules ignored: `rclpy`, `std_msgs`, `geometry_msgs`, `nav_msgs`, etc.
- **VS Code Integration**: Uses `python.linting.pylintEnabled` with the project's `.pylintrc`
- **Formatting**: Black (installed in pyproject.toml dependencies)

### Running Linting Locally
```bash
# Install local Python environment (macOS)
python3 -m venv .venv
source .venv/bin/activate
pip install -r pyproject.toml

# Run linting
pylint --rcfile=.pylintrc ros2_ws/src/my_py_pkg/
```

## Building and Testing

### Build Command
```bash
# Inside container
cd /root/ros2_ws
colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release
```

The `--symlink-install` flag creates symlinks to source files instead of copying, allowing faster iteration. The script uses `Release` build type for optimal performance.

### Testing
**Python packages** (my_py_pkg):
- Tests in `test/` directory using pytest
- Includes `test_flake8.py`, `test_copyright.py`, `test_pep257.py`
- Run with: `./ros2.sh "cd /root/ros2_ws && colcon test --packages-select my_py_pkg"`

**C++ packages** (my_cpp_pkg):
- Standard ROS2 C++ package testing with ament_lint
- Run with: `./ros2.sh "cd /root/ros2_ws && colcon test --packages-select my_cpp_pkg"`

## Important Notes for Claude Code

1. **Use helper scripts for convenience**:
   - Use `./ros2.sh` for ROS2 development tasks
   - Use `./gazebo.sh` for Gazebo simulation tasks
   - Both scripts handle container startup, building, and environment sourcing automatically

2. **Code editing happens on macOS**: All code modifications should be made to files in `ros2_ws/src/`. These are immediately visible in both containers via volume mounting.

3. **Build artifacts**: The `build/`, `install/`, and `log/` directories are persisted in the ros2_dev container and shared with the Gazebo container.

4. **ROS2 bridge is automatic**: Both containers share `ROS_DOMAIN_ID=42` and are on the same Docker network, so ROS2 topics/services/actions are automatically shared without manual configuration.

5. **GUI access**:
   - ROS2 Dev: http://localhost:6080 (VNC: 5901)
   - Gazebo: http://localhost:6081 (VNC: 5902)
   - Use web VNC rather than a VNC client for the easiest experience

6. **Multiple terminals**: You can open multiple shells in each container. Use `./ros2.sh` for dev work and `./gazebo.sh` for simulation work.

7. **Gazebo world files**: Add custom world files to `gazebo_worlds/` directory - they're mounted into the Gazebo container at `/root/gazebo_worlds/`.

## References

- [ROS2 Jazzy Documentation](https://docs.ros.org/en/jazzy/)
- [ROS2 Package Structure](https://docs.ros.org/en/jazzy/Tutorials/Creating-Your-First-ROS2-Package.html)
- [colcon build tool](https://colcon.readthedocs.io/)
- [RViz2 Visualization](https://docs.ros.org/en/jazzy/Tutorials/Intermediate/RViz2.html)
- [Gazebo Documentation](https://gazebosim.org/docs)
- [ROS2-Gazebo Integration](https://github.com/ros-simulation/gazebo_ros_pkgs)
