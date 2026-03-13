#!/usr/bin/env python3
import rospy
import math
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from tf.transformations import euler_from_quaternion

class MoveRobot:
    def __init__(self):
        rospy.init_node("move_robot_with_odom")

        self.pub = rospy.Publisher("/cmd_vel", Twist, queue_size=10)
        rospy.Subscriber("/odom", Odometry, self.odom_callback)

        self.rate = rospy.Rate(20)

        # Odometry variables
        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0

    def odom_callback(self, msg):
        # Get position
        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y

        # Convert quaternion to Euler yaw
        q = msg.pose.pose.orientation
        (_, _, self.yaw) = euler_from_quaternion([q.x, q.y, q.z, q.w])

    def move_distance(self, distance, speed=0.2):
        """Move forward (distance>0) or backward (distance<0)"""
        start_x, start_y = self.x, self.y
        cmd = Twist()

        while not rospy.is_shutdown():
            # Compute distance traveled
            dx = self.x - start_x
            dy = self.y - start_y
            dist = math.sqrt(dx**2 + dy**2)

            # Stop condition
            if dist >= abs(distance):
                break

            # Move forward or backward
            cmd.linear.x = speed if distance > 0 else -speed
            cmd.angular.z = 0.0
            self.pub.publish(cmd)
            self.rate.sleep()

        # Stop robot
        cmd.linear.x = 0.0
        self.pub.publish(cmd)
        rospy.loginfo(f"Moved {dist:.2f} meters")

    def rotate_angle(self, angle_deg, angular_speed_deg=30):
        """Rotate a specific angle in degrees using odometry yaw"""
        angle_rad = math.radians(angle_deg)
        angular_speed = math.radians(angular_speed_deg)

        start_yaw = self.yaw
        cmd = Twist()

        # Determine direction (sign)
        direction = 1 if angle_rad > 0 else -1

        while not rospy.is_shutdown():
            # Compute change in yaw
            current_yaw = self.yaw
            delta_yaw = current_yaw - start_yaw

            # Normalize yaw change to [-pi, pi]
            delta_yaw = math.atan2(math.sin(delta_yaw), math.cos(delta_yaw))

            # Stop condition
            if abs(delta_yaw) >= abs(angle_rad):
                break

            # Rotate
            cmd.linear.x = 0.0
            cmd.angular.z = direction * angular_speed
            self.pub.publish(cmd)
            self.rate.sleep()

        # Stop rotation
        cmd.angular.z = 0.0
        self.pub.publish(cmd)
        rospy.loginfo(f"Rotated {angle_deg} degrees")
    
    def move_arc(self, radius, angle_deg, speed=0.2):
        """Move along an arc of given radius (m) and central angle (deg).
        Positive angle -> turn left, negative -> turn right."""
        angle_rad = math.radians(angle_deg)
        angular_speed = speed / radius  # ω = v / R
        direction = 1 if angle_deg > 0 else -1

        start_yaw = self.yaw
        cmd = Twist()

        while not rospy.is_shutdown():
            # Calculate yaw change
            delta_yaw = self.yaw - start_yaw
            delta_yaw = math.atan2(math.sin(delta_yaw), math.cos(delta_yaw))

            if abs(delta_yaw) >= abs(angle_rad):
                break

            cmd.linear.x = speed
            cmd.angular.z = direction * angular_speed
            self.pub.publish(cmd)
            self.rate.sleep()

        # Stop
        cmd.linear.x = 0.0
        cmd.angular.z = 0.0
        self.pub.publish(cmd)
        rospy.loginfo(f"Moved in an arc: radius={radius} m, angle={angle_deg}°")

if __name__ == "__main__":
    robot = MoveRobot()
    rospy.sleep(1)  # Wait a bit for odometry

try:
    # Move forward and turn left in an arc
    robot.move_arc(radius=1.0, angle_deg=90, speed=0.2)
    rospy.sleep(0.5)

    # Move forward again and arc right
    robot.move_arc(radius=1.5, angle_deg=-45, speed=0.25)

    rospy.loginfo("Smooth trajectory complete")

    except rospy.ROSInterruptException:
        pass
