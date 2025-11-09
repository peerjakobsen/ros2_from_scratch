#!/bin/bash
# ROS2 Development Helper Script
# Usage: ./ros2.sh [command]
# If no command provided, opens interactive shell

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🤖 ROS2 Development Environment${NC}"

# Check if container is running
if ! docker compose ps | grep -q "ros2_jazzy_dev.*Up"; then
    echo -e "${GREEN}Starting ROS2 container...${NC}"
    docker compose up -d
    sleep 3
fi

# Build workspace
echo -e "${GREEN}Building workspace...${NC}"
docker compose exec ros2_dev bash -c "
    cd /root/ros2_ws && \
    source /opt/ros/jazzy/setup.bash && \
    colcon build --cmake-args -DCMAKE_BUILD_TYPE=Release 2>&1 | grep -E '(Starting|Finished|Summary|ERROR)' || true
"

# Source the workspace
echo -e "${GREEN}Sourcing workspace...${NC}"

if [ $# -eq 0 ]; then
    # No arguments - open interactive shell
    echo -e "${GREEN}Opening interactive ROS2 shell...${NC}"
    echo -e "${BLUE}Ready! You can now run ROS2 commands like:${NC}"
    echo -e "  ros2 topic list"
    echo -e "  ros2 node list"
    echo -e "  ros2 launch demo_package demo_launch.py"
    echo -e "  rviz2"
    echo ""

    docker compose exec ros2_dev bash -c "
        source /opt/ros/jazzy/setup.bash && \
        source /root/ros2_ws/install/setup.bash && \
        bash
    "
else
    # Arguments provided - run command
    echo -e "${GREEN}Running: $@${NC}"
    docker compose exec ros2_dev bash -c "
        source /opt/ros/jazzy/setup.bash && \
        source /root/ros2_ws/install/setup.bash && \
        $@
    "
fi
