import json
import os

def save_path_to_file(path, filename="challange_1_path.txt"):
    with open(filename, 'w') as f:
        json.dump(path, f)
    print(f"Path saved: {filename}")

def load_path_from_file(filename="challange_1_path.txt"):
    if not os.path.exists(filename):
        print("No existing path found. Need to discover maze first.")
        return None

    with open(filename, 'r') as f:
        path_data = json.load(f)

    path = [tuple(point) for point in path_data]

    print("Loaded existing path from path.txt")
    print(f"  Path length: {len(path)} waypoints")
    print(f"  Path: {path}")

    return path

def save_paths_to_file(path_segments, filename="challange_2_paths.txt"):
    with open(filename, 'w') as f:
        json.dump(path_segments, f)
    print(f"Path segments saved: {len(path_segments)} segments,  {filename}")

def load_paths_from_file(filename="challange_2_paths.txt"):
    if not os.path.exists(filename):
        print("No existing path found. Need to discover maze first.")
        return None

    with open(filename, 'r') as f:
        segments_data = json.load(f)

    # Convert back to tuples
    path_segments = []
    for segment in segments_data:
        path_segments.append([tuple(point) for point in segment])

    print(f"Path segments loaded: {len(path_segments)} segments, {filename}")
    return path_segments


def optimize_path(path):

    if len(path) <= 2:
        return path

    optimized = [path[0]]  # Always keep start point

    for i in range(1, len(path) - 1):
        prev_point = path[i - 1]
        current_point = path[i]
        next_point = path[i + 1]

        # Calculate direction vectors
        dx1 = current_point[0] - prev_point[0]
        dy1 = current_point[1] - prev_point[1]

        dx2 = next_point[0] - current_point[0]
        dy2 = next_point[1] - current_point[1]

        # Keep point if direction changes
        if dx1 != dx2 or dy1 != dy2:
            optimized.append(current_point)

    optimized.append(path[-1])  # Always keep end point

    return optimized
