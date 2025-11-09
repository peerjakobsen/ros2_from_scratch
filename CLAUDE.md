# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **ROS2 Jazzy Development Environment** for Apple Silicon (ARM64) with Docker support. It provides a containerized Ubuntu environment with:
- ROS2 Jazzy on ARM64 architecture
- Full XFCE desktop GUI accessible via VNC/noVNC web interface
- Pre-installed tools: RViz2, rqt, Gazebo, Navigation2
- Hot-reload development with local `src/` folder mounted into container

The project contains a Docker Compose setup that runs a complete ROS2 development environment, with two example ROS2 packages (Python and C++) to demonstrate package structure.

## Quick Commands

### Starting and Accessing the Environment

```bash
# Recommended: Use the helper script (handles container startup and workspace sourcing)
./ros2.sh                                    # Open interactive ROS2 shell
./ros2.sh "ros2 topic list"                 # Run specific ROS2 commands
./ros2.sh "ros2 launch demo_package demo_launch.py"

# Manual Docker commands
docker compose up -d                         # Start container in background
docker compose logs -f                       # View container logs
docker compose down                          # Stop container
docker compose exec ros2_dev bash            # Execute commands in running container
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

- **Web VNC (Recommended)**: Open http://localhost:6080 in your browser
- **VNC Client**: Connect to `vnc://localhost:5901` (password: `password`)
- After connecting, run `rviz2` or `rqt` to access GUI tools

## Architecture

### Directory Structure

```
ros2_from_scratch/
├── Dockerfile                 # Builds ARM64 Ubuntu image with ROS2 Jazzy
├── docker-compose.yml         # Orchestrates container with volumes and ports
├── ros2.sh                    # Helper script for convenient ROS2 command execution
├── .pylintrc                  # Python linting configuration
├── .vscode/settings.json      # VS Code Python formatter/linter settings
├── ros2_ws/
│   ├── src/                   # ROS2 package source code
│   │   ├── my_py_pkg/         # Example Python package (ament_python)
│   │   └── my_cpp_pkg/        # Example C++ package (ament_cmake)
│   ├── build/                 # Generated build files (container-only)
│   ├── install/               # Installed packages (container-only)
│   └── log/                   # Build logs (container-only)
└── pyproject.toml             # Local Python dev tools (pylint, black, isort)
```

### Key Components

#### Docker Container Setup
- **Image**: Ubuntu (ARM64) with ROS2 Jazzy, XFCE desktop, VNC server
- **Volume Mounts**:
  - `src/` — mounted as read-write (code changes sync immediately)
  - `build/`, `install/`, `log/` — container-internal (rebuilt on each startup)
- **Ports**: 5901 (VNC), 6080 (noVNC web)
- **Environment Variables**: `AUTO_BUILD=1` (auto-build on startup), `AUTO_LAUNCH=0` (don't auto-launch)

#### ROS2 Packages
- **my_py_pkg**: Python package using `ament_python` build type
  - Entry point: `test_node` command maps to `my_py_pkg.my_first_node:main`
  - Tests use pytest; linting configured in `.pylintrc`
- **my_cpp_pkg**: C++ package using `ament_cmake` build type
  - Uses rclcpp library for C++ ROS2 development

#### Helper Script (ros2.sh)
The `ros2.sh` script automates the development workflow:
1. Checks if container is running; starts it if needed
2. Runs `colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release`
3. Sources ROS2 and workspace setup files
4. Either opens an interactive shell or runs the provided command

This eliminates the need to manually source environment files for each command.

## Development Workflow

### Local Code Editing → Container Building

1. **Edit code locally** on macOS using your preferred editor (the `src/` folder is mounted)
2. **Run ./ros2.sh** to automatically:
   - Start the container if needed
   - Build the workspace
   - Open an interactive shell or run a command
3. **Changes in src/ are immediately visible** in the container due to volume mounting
4. **Build artifacts** (build/, install/, log/) stay in the container and are rebuilt on each ros2.sh invocation

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

1. **Always use ./ros2.sh for convenience**: Instead of managing Docker commands directly, use the helper script which handles container startup, building, and environment sourcing automatically.

2. **Code editing happens on macOS**: All code modifications should be made to files in `ros2_ws/src/`. These are immediately visible in the container via volume mounting.

3. **Don't persist build artifacts locally**: The `build/`, `install/`, and `log/` directories live in the container. Don't try to edit these locally—they're regenerated on each build.

4. **ROS2 package structure**: Python packages use `ament_python`, C++ use `ament_cmake`. Both require `package.xml` for metadata. The helper script handles all sourcing automatically.

5. **GUI access**: Use http://localhost:6080 (web VNC) rather than a VNC client for the easiest GUI experience.

6. **Multiple terminals**: You can open multiple container shells with `./ros2.sh` in different local terminals. Each will rebuild the workspace (idempotent with `--symlink-install`).

## References

- [ROS2 Jazzy Documentation](https://docs.ros.org/en/jazzy/)
- [ROS2 Package Structure](https://docs.ros.org/en/jazzy/Tutorials/Creating-Your-First-ROS2-Package.html)
- [colcon build tool](https://colcon.readthedocs.io/)
- [RViz2 Visualization](https://docs.ros.org/en/jazzy/Tutorials/Intermediate/RViz2.html)
