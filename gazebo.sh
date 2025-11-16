#!/bin/bash
# Gazebo Simulation Helper Script
# Usage: ./gazebo.sh [command]
# If no command provided, opens interactive shell

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Gazebo Simulation Environment${NC}"

# Check if container is running
if ! docker compose ps | grep -q "ros2_gazebo.*Up"; then
    echo -e "${GREEN}Starting Gazebo container...${NC}"
    docker compose up -d gazebo
    sleep 3
fi

# Source the workspace
echo -e "${GREEN}Preparing Gazebo environment...${NC}"

if [ $# -eq 0 ]; then
    # No arguments - open interactive shell
    echo -e "${GREEN}Opening interactive Gazebo shell...${NC}"
    echo -e "${BLUE}Ready! You can now run Gazebo commands like:${NC}"
    echo -e "  gz sim                               # Launch Gazebo"
    echo -e "  ros2 launch gazebo_ros gazebo.launch.py"
    echo -e "  ros2 topic list                      # See topics from both containers"
    echo ""
    echo -e "${BLUE}Access Gazebo GUI at: http://localhost:6081${NC}"
    echo ""

    docker compose exec gazebo bash -c "
        source /opt/ros/jazzy/setup.bash && \
        if [ -f /root/ros2_ws/install/setup.bash ]; then
            source /root/ros2_ws/install/setup.bash
        fi && \
        bash
    "
else
    # Arguments provided - run command
    echo -e "${GREEN}Running: $@${NC}"
    docker compose exec gazebo bash -c "
        source /opt/ros/jazzy/setup.bash && \
        if [ -f /root/ros2_ws/install/setup.bash ]; then
            source /root/ros2_ws/install/setup.bash
        fi && \
        $@
    "
fi
