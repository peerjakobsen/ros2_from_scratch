# Gazebo Quick Start Guide

## Launch the Fun World

Open your browser and go to **http://localhost:6081** to see the Gazebo GUI!

Then launch the world with colorful shapes:

```bash
./gazebo.sh "gz sim /root/gazebo_worlds/simple_shapes.sdf"
```

You'll see:
- 🟥 Red box (center)
- 🔵 Blue sphere (front right)
- 🟢 Green cylinder (front left)
- 🟡 Yellow capsule (back)

## Fun Things to Try

### 1. Interact with Objects in the GUI

**Open http://localhost:6081** and try these:

1. **Click PLAY** (▶️) at the bottom to start physics simulation
2. **Use the transform tools** on the left to:
   - Move objects around
   - Rotate them
   - Scale them
3. **Right-click on any object** to see options like delete, rename, etc.
4. **Click and drag the view** to rotate the camera
5. **Scroll to zoom** in and out

Watch the colored shapes fall and collide when you hit PLAY!

### 2. Apply Force to Objects (Make them move!)

Push the red box:
```bash
./gazebo.sh "gz topic -t /world/simple_shapes/link/red_box/box_link/wrench -m gz.msgs.EntityWrench -p 'entity: {name: \"red_box::box_link\"}, wrench: {force: {x: 100.0}}'"
```

Push the blue sphere:
```bash
./gazebo.sh "gz topic -t /world/simple_shapes/link/blue_sphere/sphere_link/wrench -m gz.msgs.EntityWrench -p 'entity: {name: \"blue_sphere::sphere_link\"}, wrench: {force: {x: -50.0, y: 50.0}}'"
```

Spin the green cylinder:
```bash
./gazebo.sh "gz topic -t /world/simple_shapes/link/green_cylinder/cylinder_link/wrench -m gz.msgs.EntityWrench -p 'entity: {name: \"green_cylinder::cylinder_link\"}, wrench: {torque: {z: 50.0}}'"
```

### 2. Monitor the Simulation

List all Gazebo topics:
```bash
./gazebo.sh "gz topic -l"
```

Watch object positions update in real-time:
```bash
./gazebo.sh "gz topic -e -t /world/simple_shapes/pose/info"
```

### 3. ROS2 Integration

Run the demo ROS2 node that communicates with Gazebo:
```bash
./ros2.sh "ros2 run gazebo_demos spawn_box"
```

List ROS2 topics (works from both containers):
```bash
./ros2.sh "ros2 topic list"
./gazebo.sh "ros2 topic list"
```

### 4. Using the GUI

In the browser (http://localhost:6081):
- **Click and drag** to rotate the view
- **Right-click and drag** to pan
- **Scroll** to zoom
- **Click the play button** (▶️) at the bottom to start physics simulation
- **Use the transform tools** on the left to move objects around

### 5. Create Your Own Shapes

You can modify `/gazebo_worlds/simple_shapes.sdf` to add more objects or change colors!

Example - add a purple box:
```xml
<model name="purple_box">
  <pose>3 0 0.5 0 0 0</pose>
  <link name="link">
    <collision name="collision">
      <geometry>
        <box><size>0.5 0.5 0.5</size></box>
      </geometry>
    </collision>
    <visual name="visual">
      <geometry>
        <box><size>0.5 0.5 0.5</size></box>
      </geometry>
      <material>
        <ambient>0.5 0 0.5 1</ambient>
        <diffuse>0.5 0 0.5 1</diffuse>
      </material>
    </visual>
  </link>
</model>
```

## Next Steps

- Create robot models (URDF/SDF)
- Add sensors (cameras, lidars)
- Build autonomous navigation
- Simulate robot arms
- Test control algorithms

Have fun experimenting! 🚀
