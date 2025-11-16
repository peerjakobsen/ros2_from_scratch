#!/bin/bash
# Spawn a random colored box in Gazebo
# Usage: ./spawn_random_box.sh

# Random position (using LC_NUMERIC=C to force period as decimal separator)
X=$(LC_NUMERIC=C awk -v min=-3 -v max=3 'BEGIN{srand(); print min+rand()*(max-min)}')
Y=$(LC_NUMERIC=C awk -v min=-3 -v max=3 'BEGIN{srand(); print min+rand()*(max-min)}')
Z=$(LC_NUMERIC=C awk -v min=0.5 -v max=2.0 'BEGIN{srand(); print min+rand()*(max-min)}')

# Random size
SIZE=$(LC_NUMERIC=C awk -v min=0.3 -v max=1.0 'BEGIN{srand(); print min+rand()*(max-min)}')

# Random color
R=$(LC_NUMERIC=C awk 'BEGIN{srand(); print rand()}')
G=$(LC_NUMERIC=C awk 'BEGIN{srand(); print rand()}')
B=$(LC_NUMERIC=C awk 'BEGIN{srand(); print rand()}')

# Unique name with timestamp
MODEL_NAME="box_$(date +%s)_$$"

echo "Spawning $MODEL_NAME at ($X, $Y, $Z) with size $SIZE"

# Create the SDF file inside the container
docker compose exec -T gazebo bash << EOFMAIN
cat > /tmp/${MODEL_NAME}.sdf << 'EOFSDF'
<?xml version="1.0" ?>
<sdf version="1.8">
  <model name="${MODEL_NAME}">
    <pose>${X} ${Y} ${Z} 0 0 0</pose>
    <link name="link">
      <inertial>
        <mass>1.0</mass>
        <inertia>
          <ixx>0.166667</ixx>
          <iyy>0.166667</iyy>
          <izz>0.166667</izz>
        </inertia>
      </inertial>
      <collision name="collision">
        <geometry>
          <box>
            <size>${SIZE} ${SIZE} ${SIZE}</size>
          </box>
        </geometry>
      </collision>
      <visual name="visual">
        <geometry>
          <box>
            <size>${SIZE} ${SIZE} ${SIZE}</size>
          </box>
        </geometry>
        <material>
          <ambient>${R} ${G} ${B} 1</ambient>
          <diffuse>${R} ${G} ${B} 1</diffuse>
          <specular>0.5 0.5 0.5 1</specular>
        </material>
      </visual>
    </link>
  </model>
</sdf>
EOFSDF

# Now spawn it using the file
gz service -s /world/simple_shapes/create \
  --reqtype gz.msgs.EntityFactory \
  --reptype gz.msgs.Boolean \
  --timeout 1000 \
  --req "sdf_filename: \"/tmp/${MODEL_NAME}.sdf\""
EOFMAIN

echo "✓ Box spawned successfully!"
echo "Open http://localhost:6081 to see it in the Gazebo GUI"
