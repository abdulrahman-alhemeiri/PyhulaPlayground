from libs.Drone import Drone

drone = Drone()
drone.take_off()

path = [(6,6), (5,6), (5,5), (4, 5), (4,4)]
# path = [(6,6), (6,4), (4,4)]
# path = [(6,6), (6,0), (4,0), (4,4)]

drone.traverse_path(path)
drone.land()
