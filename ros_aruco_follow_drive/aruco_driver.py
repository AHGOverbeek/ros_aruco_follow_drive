"""
ROS2 subscriber + publisher node, for reading Aruco data
and generating drive commands.
"""

import rclpy
from rclpy.node import Node
from nakama_eve_interfaces.msg import ArucoData
from halodi_msgs.msg import DrivingCommand

def aruco_tracking(id_in_view = False, id_position_x = 0.0, id_position_y = 0.0):

    # set velocity commands to zero at start, to be sure if forgetting to assign
    linear_velocity_command = 0.0
    angular_velocity_command = 0.0

    if id_in_view:
        print("Marker of interest in view at positions: {0}, {1}".format(id_position_x, id_position_y))

        # # example code
        # # rotate towards marker when it is not in the middle of the robot's view
        # angular_velocity_command = id_position_x/100 
        # # drive towards 2 meters(?) distance with on-off/BANG-BANG control
        # if id_position_y < 2:
        #     linear_velocity_command = 0.1
        # elif id_position_y > 2:
        #     linear_velocity_command = -0.1

    else:
        # if not in view, do nothing for now
        print("Marker of interest is not in view, do nothing for now")
        
    print("Driving command is: {0}, {1}".format(linear_velocity_command, angular_velocity_command))

    return linear_velocity_command, angular_velocity_command

# ------------------------------------------------------------------------------------------
# Danger, do not go beyond this point ;)
# ------------------------------------------------------------------------------------------

class ArucoDriver(Node):
    
    def __init__(self):
        super().__init__('aruco_driver')

        self.subscriber_aruco_data = self.create_subscription(
            ArucoData, "aruco_data", self.aruco_data_callback, rclpy.qos.qos_profile_system_default)
            
        self.publisher_driving_command = self.create_publisher(
            DrivingCommand, 'eve/driving_command', rclpy.qos.qos_profile_system_default)
        
        # the marker id to track
        self.id = 1

        # some offsets because calibration is not proper
        self.x_offset = 0.0
        self.y_offset = 0.0

        return


    def aruco_data_callback(self, msg):
        
        # to lists
        self.marker_ids = list(msg.marker_ids)
        self.bounding_boxes = list(msg.bounding_boxes)
        self.translation_vectors = list(msg.translation_vectors)
        self.rotation_vectors = list(msg.rotation_vectors)

        #TODO: is there a way to assign every marker to its own class? Maybe not because they might appear and disappear

        # see if the marker of interest is in view
        if self.id in self.marker_ids:
            self.id_in_view = True

            # find where the intersting id is in the marker_ids
            self.id_index = self.marker_ids.index(self.id)
            
            # get only the data we're interesting in, TODO: better way to do this?
            self.id_bounding_boxes = self.bounding_boxes[(self.id_index*8):(self.id_index*8 + 8)] # 8 ints, a pair for each x and y for each marker
            self.id_translation_vectors = self.translation_vectors[(self.id_index*3):(self.id_index*3 + 3)] # 3 cartesian coordinates for each marker
            self.id_rotation_vectors = self.rotation_vectors[(self.id_index*3):(self.id_index*3 + 3)] # 3 rotation coordinates for each marker

        else:
            self.id_in_view = False

        # function to track
        # send x and y, receive lin and angular velocity commands
        # flip the sign of y because it seems opposite
        self.linear_velocity, self.angular_velocity = aruco_tracking(self.id_in_view, self.id_translation_vectors[0] + self.x_offset, 1 - self.id_translation_vectors[1] + self.y_offset)

        # publish command
        msg = DrivingCommand()
        msg.linear_velocity = self.linear_velocity
        msg.angular_velocity = self.angular_velocity
        self.publisher_driving_command.publish(msg)

        return

def main(args=None):

    rclpy.init(args=args)

    aruco_driver = ArucoDriver()

    # Get out of spin with ctrl+c    
    try:
        rclpy.spin(aruco_driver)
    except KeyboardInterrupt:
        pass
    
    aruco_driver.destroy_node()
    rclpy.shutdown()
    

if __name__ == "__main__":
    main()
