#!/bin/bash
# Make it rain boxes in Gazebo!
# Usage: ./box_rain.sh [number_of_boxes]

NUM_BOXES=${1:-10}

echo "🌧️  Making it rain $NUM_BOXES boxes!"
echo "Open http://localhost:6081 and click PLAY to see them fall!"
echo ""

for i in $(seq 1 $NUM_BOXES); do
    echo "Spawning box $i/$NUM_BOXES..."
    ./spawn_random_box.sh
    sleep 0.5
done

echo ""
echo "✓ Done! $NUM_BOXES boxes spawned!"
echo "Watch them fall and collide in the Gazebo GUI!"
