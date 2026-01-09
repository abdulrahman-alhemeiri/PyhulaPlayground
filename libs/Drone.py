from typing import List, Any

import pyhula
import time
import math
import sys
import cv2
import os

from hula_video import hula_video
from onnxdetector import onnxdetector
from datetime import datetime, timezone

HEIGHT = 100
SLEEP_VALUE = 0.8
OBJECT_DETECTION_MAX_TRIES = 1000
LOGS_ENABLED = False

class Drone:
    def __init__(self, bearing="North"):
        self.api = pyhula.UserApi()
        if not self.api.connect():
            print("connect error!!!!!!!")
            sys.exit(0)
        else:
            print("connection to station by wifi")
        self.api.Plane_cmd_camera_angle(4, 0)
        self.vid = hula_video(hula_api = self.api, display = False)
        self.huladetector = onnxdetector(model="detect_3_object_12_11.onnx", label="object.txt", confidence_thres=0.65)
        self.current_bearing = bearing
        time.sleep(2)

    def move_to_coordinates(self, x, y, z):
        print(f"move_to_coordinates()::: moving to coordinates: [X: {x}, Y: {y}, Z: {z}]" if LOGS_ENABLED else "")
        self.api.single_fly_straight_flight(x, y, z, 60)
        time.sleep(SLEEP_VALUE)

    def take_off(self, video_mode = False):
        print("+++++ taking off")
        self.api.Plane_cmd_switch_QR(0)
        time.sleep(SLEEP_VALUE)
        self.api.single_fly_barrier_aircraft(True)
        time.sleep(SLEEP_VALUE)
        if video_mode:
            self.vid.video_mode_on()
            time.sleep(SLEEP_VALUE)

        self.api.single_fly_takeoff()
        time.sleep(SLEEP_VALUE)

    def land(self, video_mode = False):
        print("----- landing")
        self.api.single_fly_touchdown()
        if video_mode:
            self.vid.close()

    def center_at_current_block(self):
        print(f"center_at_current_block()::: centering at current block" if LOGS_ENABLED else "")
        x, y, z = self.api.get_coordinate()
        print(f"center_at_current_block()::: current coordinates: [X: {x}, Y: {y}, Z: {z}]" if LOGS_ENABLED else "")

        if x < 0:
            x = 0
        if y < 0:
            y = 0
        print(f"center_at_current_block()::: after zeroing: [X: {x}, Y: {y}, Z: {z}]" if LOGS_ENABLED else "")

        center_x = math.floor(x / 60.0) * 60 + 15
        center_y = math.floor(y / 60.0) * 60 + 15
        print(f"center_at_current_block()::: center coordinates: [X: {center_x}, Y: {center_y}, Z: {z}" if LOGS_ENABLED else "")
        self.move_to_coordinates(center_x, center_y, z)

    def center_yaw(self):
        print("center_yaw()::: centering yaw" if LOGS_ENABLED else "")
        yaw, pitch, roll = self.api.get_yaw()
        print(f"center_yaw()::: current yaw: {yaw}" if LOGS_ENABLED else "")
        if yaw > 0:
            print("center_yaw()::: turning right" if LOGS_ENABLED else "")
            self.api.single_fly_turnleft(yaw)
        if yaw < 0:
            print("center_yaw()::: turning left" if LOGS_ENABLED else "")
            self.api.single_fly_turnright(yaw * -1)

    def move_to_block(self, x, y):
        print(f"move_to_block()::: moving to block: [X: {x}, Y: {y}]" if LOGS_ENABLED else "")
        current_block = self.get_current_block()
        print(f"move_to_block()::: current block: [X: {current_block[0]}, Y: {current_block[0]}]" if LOGS_ENABLED else "")

        if current_block[0] == x and current_block[1] == y:
            print(f"move_to_block()::: already at target block" if LOGS_ENABLED else "")
            return

        target_x = 60 * x + 15
        target_y = 60 * y + 15
        print(f"move_to_block()::: target coordinates: [X: {target_x}, Y: {target_y}]" if LOGS_ENABLED else "")
        self.move_to_coordinates(target_x, target_y, HEIGHT)

    def get_barriers(self):
        print(f"get_barriers()::: getting current barriers" if LOGS_ENABLED else "")
        obstacles = self.api.Plane_getBarrier()
        result = []
        bearing_dictionary = {
            "North": {
                "forward": "forward",
                "left": "left",
                "back": "back",
                "right": "right"
            },
            "West": {
                "forward": "left",
                "left": "back",
                "back": "right",
                "right": "forward"
            },
            "South": {
                "forward": "back",
                "left": "right",
                "back": "forward",
                "right": "left"
            },
            "East": {
                "forward": "right",
                "left": "forward",
                "back": "left",
                "right": "back"
            }
        }

        if obstacles["forward"]:
            result.append(bearing_dictionary[self.current_bearing]["forward"])
        if obstacles["back"]:
            result.append(bearing_dictionary[self.current_bearing]["back"])
        if obstacles["right"]:
            result.append(bearing_dictionary[self.current_bearing]["right"])
        if obstacles["left"]:
            result.append(bearing_dictionary[self.current_bearing]["left"])

        print((f"get_barriers()::: Obstacles found: " + str(result)) if LOGS_ENABLED else "")

        return result

    def get_current_block(self) -> List[Any]:
        print(f"get_current_block()::: getting current block" if LOGS_ENABLED else "")
        x, y, z = self.api.get_coordinate()
        print(f"get_current_block()::: current coordinates: [X: {x}, Y: {y}, Z: {z}]" if LOGS_ENABLED else "")
        block_x = math.floor(x / 60.0)
        block_y = math.floor(y / 60.0)
        print(f"get_current_block()::: current block: [X: {block_x}, Y: {block_y}]" if LOGS_ENABLED else "")
        return [block_x, block_y]

    def traverse_path(self, path):
        for x, y in path:
            self.move_to_block(x, y)

    def turn_to_bearing(self, direction):
        if self.current_bearing == "North":
            if direction == "West":
                self.api.single_fly_turnleft(90)
            elif direction == "South":
                self.api.single_fly_turnleft(180)
            elif direction == "East":
                self.api.single_fly_turnright(90)
        elif self.current_bearing == "West":
            if direction == "South":
                self.api.single_fly_turnleft(90)
            elif direction == "East":
                self.api.single_fly_turnleft(180)
            elif direction == "North":
                self.api.single_fly_turnright(90)
        elif self.current_bearing == "South":
            if direction == "East":
                self.api.single_fly_turnleft(90)
            elif direction == "North":
                self.api.single_fly_turnleft(180)
            elif direction == "West":
                self.api.single_fly_turnright(90)
        elif self.current_bearing == "East":
            if direction == "North":
                self.api.single_fly_turnleft(90)
            elif direction == "West":
                self.api.single_fly_turnleft(180)
            elif direction == "South":
                self.api.single_fly_turnright(90)

        self.current_bearing = direction
        return

    def perform_detection(self, direction):
        print(f"+++++ Performing object detection at direction {direction}")
        self.turn_to_bearing(direction)
        current_block = self.get_current_block()
        cell_file_name = f"Cell({current_block[0]}, {current_block[1]})_{direction}_"
        self.vid.startrecording(cell_file_name)
        object_found = False
        for i in range(OBJECT_DETECTION_MAX_TRIES):
            frame = self.vid.get_video()
            obj_found, frame = self.huladetector.detect(frame)
            if not obj_found is None:
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                filename = f"{obj_found['label']}_{cell_file_name}{timestamp}.jpg"
                savepath = os.path.join(os.getcwd(), '../detected_objects')
                cv2.imwrite(os.path.join(savepath, filename), frame)
                print(f"Found {obj_found}")
                print(f"Saving to file: {filename}")
                object_found = True
                break

        print(f"Object found? {object_found}")
        self.vid.stoprecording()
        # self.center_yaw()
