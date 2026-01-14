import pyhula
import time
import math
import sys
import cv2
import os
import Utils

from .hula_video import hula_video
from .onnxdetector import onnxdetector
from datetime import datetime, timezone

DEFAULT_HEIGHT = 95
DESCENDING_INCREMENTAL_VALUE = 3
MINIMUM_HEIGHT = 65
LAST_STEP_HEIGHT = 40

SPEED = 100
SLEEP_BASE_VALUE = 0.4
SLEEP_INCREMENT_VALUE = 0.1
SLEEP_VALUE = 0.8

OBJECT_DETECTION_MAX_TRIES = 100

LOGS_ENABLED = True
def LOG(message):
    if LOGS_ENABLED:
        print(message)

class Drone:
    def __init__(self, bearing="North", challenge=1, phase=1):
        self.api = pyhula.UserApi()
        if not self.api.connect():
            print("connect error!!!!!!!")
            sys.exit(0)
        else:
            print("connection to station by wifi")

        self.challenge_number = challenge
        self.phase_number = phase
        self.current_bearing = bearing
        self.challenge_height = DEFAULT_HEIGHT

        if self.phase_number == 1:
            self.api.single_fly_barrier_aircraft(True)
            time.sleep(SLEEP_VALUE)

        if self.challenge_number == 2 and self.phase_number == 2:
            self.api.Plane_cmd_camera_angle(4, 0)
            self.vid = hula_video(hula_api = self.api, display = False)
            self.huladetector = onnxdetector(model="detect_3_object_12_11.onnx", label="object.txt", confidence_thres=0.4)
            self.vid.video_mode_on()

        self.api.Plane_cmd_switch_QR(0)
        time.sleep(SLEEP_VALUE)
        print(f"Started challenge: {self.challenge_number}")
        time.sleep(2)

    def take_off(self):
        print("+++++ taking off")
        time.sleep(SLEEP_VALUE)
        self.api.single_fly_takeoff()
        time.sleep(SLEEP_VALUE)

    def land(self):
        print("----- landing")
        self.api.single_fly_touchdown()
        if self.challenge_number == 2:
            self.vid.close()

    def move_to_coordinates(self, x, y, z, sleep=SLEEP_VALUE):
        LOG(f"move_to_coordinates()::: moving to coordinates: [X: {x}, Y: {y}, Z: {z}]")
        self.api.single_fly_straight_flight(x, y, z, SPEED)
        time.sleep(sleep)

    def move_to_block(self, x, y, z=DEFAULT_HEIGHT, is_last_step=False):
        LOG(f"move_to_block()::: moving to block: [X: {x}, Y: {y}]")
        current_block = self.get_current_block()
        LOG(f"move_to_block()::: current block: [X: {current_block[0]}, Y: {current_block[0]}]")

        if current_block[0] == x and current_block[1] == y:
            LOG(f"move_to_block()::: already at target block")
            return

        movement_length = Utils.length(current_block, (x,y))
        sleep_value = SLEEP_BASE_VALUE + (movement_length * SLEEP_INCREMENT_VALUE)

        target_x = 60 * x + 15
        target_y = 60 * y + 15
        LOG(f"move_to_block()::: target coordinates: [X: {target_x}, Y: {target_y}], Z:{z}")
        if is_last_step:
            z = LAST_STEP_HEIGHT
        self.move_to_coordinates(target_x, target_y, z, sleep_value)

    def traverse_path(self, path):
        if self.challenge_number == 1:
            index = 0
            for x, y in path:
                self.challenge_height = self.challenge_height - DESCENDING_INCREMENTAL_VALUE
                if self.challenge_height < MINIMUM_HEIGHT:
                    self.challenge_height = MINIMUM_HEIGHT

                is_last_step = False
                if (index == len(path) - 1):
                    is_last_step = True
                self.move_to_block(x, y, self.challenge_height, is_last_step)
                index = index + 1

        if self.challenge_number == 2:
            for x, y in path:
                self.move_to_block(x, y, DEFAULT_HEIGHT)

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

    def perform_detection(self, direction, on_object_found=None, on_progress=None):
        print(f"+++++ Performing object detection at direction {direction}")
        self.turn_to_bearing(direction)
        current_block = self.get_current_block()
        cell_file_name = f"Cell({current_block[0]}, {current_block[1]})_{direction}_"
        self.center_at_current_block()
        self.vid.startrecording(cell_file_name)
        object_found = False
        for i in range(OBJECT_DETECTION_MAX_TRIES):
            frame = self.vid.get_video()
            LOG(f"started self.huladetector.detect(frame)")
            obj_found, frame = self.huladetector.detect(frame)
            LOG(f"ended self.huladetector.detect(frame)")

            if not obj_found is None:
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                filename = f"{obj_found['label']}_{cell_file_name}{timestamp}.jpg"
                savepath = os.path.join(os.getcwd(), 'detected_objects')
                cv2.imwrite(os.path.join(savepath, filename), frame)
                print(f"Found {obj_found} after {i + 1} tries")
                print(f"Saving to file: {filename}")
                object_found = True
                on_object_found(obj_found['label'], direction, current_block)
                break

        if not object_found:
            print(f"Object NOT FOUND!")

        self.vid.stoprecording()

    def get_barriers(self):
        LOG(f"get_barriers()::: getting current barriers")
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

        LOG(f"get_barriers()::: Obstacles found: " + str(result))

        return result

    def get_current_block(self):
        LOG(f"get_current_block()::: getting current block")
        x, y, z = self.api.get_coordinate()
        LOG(f"get_current_block()::: current coordinates: [X: {x}, Y: {y}, Z: {z}]")
        block_x = math.floor(x / 60.0)
        if block_x < 0:
            block_x = 0
        block_y = math.floor(y / 60.0)
        if block_y < 0:
            block_y = 0
        LOG(f"get_current_block()::: current block: [X: {block_x}, Y: {block_y}]")
        return block_x, block_y

    def center_at_current_block(self):
        LOG(f"center_at_current_block()::: centering at current block")
        x, y, z = self.api.get_coordinate()
        LOG(f"center_at_current_block()::: current coordinates: [X: {x}, Y: {y}, Z: {z}]")

        if x < 0:
            x = 0
        if y < 0:
            y = 0
        LOG(f"center_at_current_block()::: after zeroing: [X: {x}, Y: {y}, Z: {z}]")

        center_x = math.floor(x / 60.0) * 60 + 15
        center_y = math.floor(y / 60.0) * 60 + 15
        LOG(f"center_at_current_block()::: center coordinates: [X: {center_x}, Y: {center_y}, Z: {z}")
        self.move_to_coordinates(center_x, center_y, z)

    def center_yaw(self):
        LOG("center_yaw()::: centering yaw")
        yaw, pitch, roll = self.api.get_yaw()
        LOG(f"center_yaw()::: current yaw: {yaw}")
        if yaw > 0:
            LOG("center_yaw()::: turning right")
            self.api.single_fly_turnleft(yaw)
        if yaw < 0:
            LOG("center_yaw()::: turning left")
            self.api.single_fly_turnright(yaw * -1)
