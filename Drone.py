import pyhula
import time
import math
import sys
from hula_video import hula_video
from onnxdetector import onnxdetector

SLEEP_VALUE = 1

class Drone:
    def __init__(self):
        self.api = pyhula.UserApi()
        if not self.api.connect():
            print("connect error!!!!!!!")
            sys.exit(0)
        else:
            print("connection to station by wifi")
        self.vid = hula_video(hula_api = self.api, display = False)
        self.huladetector = onnxdetector(model="detect_3_object_12_11.onnx", label="object.txt", confidence_thres=0.65)

    def move_to_coordinates(self, x, y, z):
        print(f"move_to_coordinates()::: moving to coordinates: [X: {x}, Y: {y}, Z: {z}]")
        self.api.single_fly_straight_flight(x, y, z, 60)
        time.sleep(SLEEP_VALUE)

    def move_to_elevation(self, z):
        print(f"move_to_elevation()::: moving to elevation {z}")
        c = self.api.get_coordinate()
        self.move_to_coordinates(c[0], c[1], z)

    def take_off(self, video_mode = False):
        print("---------taking off")
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
        print("---------landing")
        self.api.single_fly_touchdown()
        if video_mode:
            self.vid.close()

    def center_at_current_block(self):
        print("center_at_current_block()::: centering at current block")
        x, y, z = self.api.get_coordinate()
        print(f"center_at_current_block()::: current coordinates: [X: {x}, Y: {y}, Z: {z}]")

        if x < 0:
            x = 0
        if y < 0:
            y = 0
        print(f"center_at_current_block()::: after zeroing: [X: {x}, Y: {y}, Z: {z}]")

        center_x = math.floor(x / 60.0) * 60 + 15
        center_y = math.floor(y / 60.0) * 60 + 15
        print(f"center_at_current_block()::: center coordinates: [X: {center_x}, Y: {center_y}, Z: {z}")
        self.move_to_coordinates(center_x, center_y, z)

    def center_yaw(self):
        print("center_yaw()::: centering yaw")
        yaw, pitch, roll = self.api.get_yaw()
        print(f"center_yaw()::: current yaw: {yaw}")
        if yaw > 0:
            print("center_yaw()::: turning right")
            self.api.single_fly_turnleft(yaw)
        if yaw < 0:
            print("center_yaw()::: turning left")
            self.api.single_fly_turnright(yaw * -1)

    def move_to_block(self, x, y):
        print(f"move_to_block()::: moving to block: [X: {x}, Y: {y}]")

        current_block = self.get_current_block()
        print(f"move_to_block()::: current block: [X: {current_block[0]}, Y: {current_block[0]}]")

        if current_block[0] == x and current_block[1] == y:
            print(f"move_to_block()::: already at target block")
            return

        target_x = 60 * x + 15
        target_y = 60 * y + 15
        print(f"move_to_block()::: target coordinates: [X: {target_x}, Y: {target_y}]")
        self.move_to_coordinates(target_x, target_y, 90)

    def get_barriers(self):
        print(f"get_barriers()::: getting current barriers")
        obstacles = self.api.Plane_getBarrier()
        result = []
        if obstacles["forward"]:
            result.append("forward")
        if obstacles["back"]:
            result.append("back")
        if obstacles["right"]:
            result.append("right")
        if obstacles["left"]:
            result.append("left")

        print(f"get_barriers()::: Obstacles found: " + str(result))

        return result

    def get_current_block(self):
        print(f"get_current_block()::: getting current block")
        x, y, z = self.api.get_coordinate()
        print(f"get_current_block()::: current coordinates: [X: {x}, Y: {y}, Z: {z}]")
        block_x = math.floor(x / 60.0)
        block_y = math.floor(y / 60.0)
        print(f"get_current_block()::: current block: [X: {block_x}, Y: {block_y}]")
        return [block_x, block_y]

    def traverse_path(self, path):
        for x, y in path:
            self.move_to_block(x, y)

    def perform_360_object_detection(self):
        current_block = self.get_current_block()
        cell_file_name = f"Cell({current_block[0]}, {current_block[1]})"
        self.vid.startrecording(cell_file_name)
        self.center_at_current_block()

        barriers = self.api.Plane_getBarrier()
        if barriers["forward"]:
            self.perform_detection()

        current_direction = "forward"
        next_direction = "forward"
        target_turn = -1
        if barriers["left"]:
            target_turn = 90
            next_direction = "left"
        elif barriers["back"]:
            target_turn = 180
            next_direction = "back"
        elif barriers["right"]:
            target_turn = 90
            next_direction = "right"

        if next_direction is "forward":
            return
        if next_direction is "right":
            self.api.single_fly_turnright(target_turn)
            time.sleep(SLEEP_VALUE)
        else:
            self.api.single_fly_turnleft(target_turn)
            time.sleep(SLEEP_VALUE)

        current_direction = next_direction

        if current_direction is "left":
            if barriers["left"]:
                self.perform_detection()

            if barriers["back"]:
                target_turn = 90
                next_direction = "back"
            elif barriers["right"]:
                target_turn = 180
                next_direction = "right"
            else:
                target_turn = 90
                next_direction = "forward"

            if next_direction is "forward":
                self.api.single_fly_turnright(target_turn)
                time.sleep(SLEEP_VALUE)
            else:
                self.api.single_fly_turnleft(target_turn)
                time.sleep(SLEEP_VALUE)

            current_direction = next_direction

        if current_direction is "back":
            if barriers["back"]:
                self.perform_detection()

            if barriers["right"]:
                target_turn = 90
                next_direction = "right"
            else:
                target_turn = 180
                next_direction = "forward"

            self.api.single_fly_turnleft(target_turn)
            time.sleep(SLEEP_VALUE)
            current_direction = next_direction

        if current_direction is "right":
            if barriers["back"]:
                self.perform_detection()
            self.api.single_fly_turnleft(90)
            time.sleep(SLEEP_VALUE)

        self.vid.stoprecording()
        time.sleep(SLEEP_VALUE)

    def perform_detection(self):
        frame = self.vid.get_video()
        obj_found, frame = self.huladetector.detect(frame)
        if not obj_found is None:
            print(f"Found {obj_found}")
