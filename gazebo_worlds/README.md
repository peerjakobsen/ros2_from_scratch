# Gazebo World Files

This directory contains Gazebo world files (SDF format) that can be loaded in the Gazebo simulation container.

## Available Worlds

- **empty_world.sdf**: A simple empty world with a ground plane and lighting
- **simple_shapes.sdf**: A fun world with colorful shapes (red box, blue sphere, green cylinder, yellow capsule)

## Usage

### Launch a specific world file:

```bash
# Empty world
./gazebo.sh "gz sim /root/gazebo_worlds/empty_world.sdf"

# World with colorful shapes (more fun!)
./gazebo.sh "gz sim /root/gazebo_worlds/simple_shapes.sdf"
```

### Launch Gazebo via ROS2:

```bash
./gazebo.sh "ros2 launch ros_gz_sim gz_sim.launch.py gz_args:=/root/gazebo_worlds/simple_shapes.sdf"
```

### Interact with the simulation from ROS2 container:

```bash
# In ROS2 container - run the demo node
./ros2.sh "ros2 run gazebo_demos spawn_box"

# List available Gazebo topics (from either container)
./gazebo.sh "gz topic -l"

# Echo a Gazebo topic
./gazebo.sh "gz topic -e -t /world/simple_shapes/pose/info"

# Apply force to the red box (make it move!)
./gazebo.sh "gz topic -t /world/simple_shapes/link/red_box/box_link/wrench -m gz.msgs.EntityWrench -p 'entity: {name: \"red_box::box_link\"}, wrench: {force: {x: 100.0, y: 0, z: 0}}'"
```

## Creating Custom Worlds

1. Add your `.sdf` world file to this directory
2. It will be automatically mounted in the Gazebo container at `/root/gazebo_worlds/`
3. Launch it using the commands above with your filename

## SDF Format

World files use the SDF (Simulation Description Format). See the [Gazebo SDF documentation](http://sdformat.org/) for more information on creating world files.

## Example: Adding a Model

To add models to your world:

1. Download models from [Gazebo Fuel](https://app.gazebosim.org/fuel/models)
2. Models are cached in a Docker volume (`gazebo_models`)
3. Reference them in your SDF world file using standard SDF syntax
