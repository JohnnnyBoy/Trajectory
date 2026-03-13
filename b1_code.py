#!/usr/bin/env python3
import rospy
import math
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from std_msgs.msg import Int32
from tf.transformations import euler_from_quaternion

class MoveRobot:
    def _init_(self):
        # Initialize node
        rospy.init_node("trajectory_node", anonymous=True)

        # Publishers & Subscribers
        self.cmd_pub = rospy.Publisher("/cmd_vel", Twist, queue_size=10)
        self.reached_pub = rospy.Publisher("/place_reached", Int32, queue_size=10)
        rospy.Subscriber("/odom", Odometry, self.odom_callback)
        rospy.Subscriber("/move_to_place", Int32, self.move_command_callback)

        # Control loop rate
        self.rate = rospy.Rate(20)  # 20 Hz

        # Odometry state
        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0

        rospy.loginfo("Trajectory node ready. Waiting for /move_to_place commands...")

    # ------------- ODOMETRY -------------
    def odom_callback(self, msg):
        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y
        q = msg.pose.pose.orientation
        (_, _, self.yaw) = euler_from_quaternion([q.x, q.y, q.z, q.w])

    # ------------- MOTION PRIMITIVES -------------
    def move_distance(self, distance, speed=0.25):
        """Move forward (distance>0) or backward (distance<0) with closed-loop control"""
        start_x, start_y = self.x, self.y
        target_dist = abs(distance)
        direction = 1 if distance > 0 else -1
        cmd = Twist()

        Kp_dist = 1.2   # proportional gain for distance
        Kp_ang = 2.0    # proportional gain for heading correction

        target_yaw = self.yaw  # maintain initial heading

        dist = 0.0
        while not rospy.is_shutdown():
            dx = self.x - start_x
            dy = self.y - start_y
            dist = math.sqrt(dx*2 + dy*2)
            if dist >= target_dist:
                break

            heading_error = math.atan2(math.sin(target_yaw - self.yaw), math.cos(target_yaw - self.yaw))
            linear_vel = direction * Kp_dist * (target_dist - dist)
            angular_vel = Kp_ang * heading_error

            # Clamp
            linear_vel = max(min(linear_vel, speed), -speed)
            angular_vel = max(min(angular_vel, 0.8), -0.8)

            cmd.linear.x = linear_vel
            cmd.angular.z = angular_vel
            self.cmd_pub.publish(cmd)
            self.rate.sleep()

        # Stop
        cmd.linear.x = 0.0
        cmd.angular.z = 0.0
        self.cmd_pub.publish(cmd)
        rospy.loginfo(f"move_distance finished: moved {dist:.2f} m (target {distance} m)")

    def rotate_angle(self, angle_deg, angular_speed_deg=30):
        """Rotate a specific angle in degrees using odometry yaw with closed-loop control"""
        angle_rad = math.radians(angle_deg)
        start_yaw = self.yaw
        target_yaw = start_yaw + angle_rad
        target_yaw = math.atan2(math.sin(target_yaw), math.cos(target_yaw))
        cmd = Twist()

        Kp_yaw = 1.5
        while not rospy.is_shutdown():
            yaw_error = math.atan2(math.sin(target_yaw - self.yaw), math.cos(target_yaw - self.yaw))
            if abs(yaw_error) < math.radians(1.5):
                break

            angular_vel = Kp_yaw * yaw_error
            max_ang_speed = math.radians(angular_speed_deg)
            angular_vel = max(min(angular_vel, max_ang_speed), -max_ang_speed)

            cmd.linear.x = 0.0
            cmd.angular.z = angular_vel
            self.cmd_pub.publish(cmd)
            self.rate.sleep()

        # Stop rotation
        cmd.angular.z = 0.0
        self.cmd_pub.publish(cmd)
        rospy.loginfo(f"rotate_angle finished: rotated {angle_deg} deg")

    # ------------- TASKS (one per place) -------------
    def task_place_1(self):
        rospy.loginfo("Task: moving to PLACE 1")
        try:
            # Adjust these distances/angles to match your map/positions
            self.move_distance(2.17, speed=0.25)
            rospy.sleep(0.2)
            self.rotate_angle(-91, angular_speed_deg=40)
            rospy.sleep(0.2)
            rospy.loginfo("Reached PLACE 1")
            self.reached_pub.publish(Int32(data=1))
        except rospy.ROSInterruptException:
            rospy.logwarn("Task PLACE 1 interrupted")

    def task_place_2(self):
        rospy.loginfo("Task: moving to PLACE 2")
        try:
            # Example trajectory — change values as needed
            self.rotate_angle(90, angular_speed_deg=40)
            rospy.sleep(0.2)
            self.move_distance(1.5, speed=0.25)
            rospy.sleep(0.2)
            self.rotate_angle(-90, angular_speed_deg=40)
            rospy.sleep(0.2)
            self.move_distance(1, speed=0.25)
            rospy.sleep(0.2)
            self.rotate_angle(90, angular_speed_deg=40)
            self.move_distance(0.5, speed=0.25)
            rospy.sleep(0.2)
            rospy.loginfo("Reached PLACE 2")
            self.reached_pub.publish(Int32(data=2))
        except rospy.ROSInterruptException:
            rospy.logwarn("Task PLACE 2 interrupted")

    def task_place_3(self):
        rospy.loginfo("Task: moving to PLACE 3")
        try:
            # Example trajectory — change values as needed
            self.rotate_angle(90, angular_speed_deg=40)
            self.move_distance(1, speed=0.25)
            rospy.sleep(0.2)
            
            rospy.sleep(0.2)
            rospy.loginfo("Reached PLACE 3")
            self.reached_pub.publish(Int32(data=3))
        except rospy.ROSInterruptException:
            rospy.logwarn("Task PLACE 3 interrupted")

    # ------------- COMMAND CALLBACK -------------
    def move_command_callback(self, msg):
        """Called when the state machine publishes /move_to_place with 1,2 or 3."""
        place = msg.data
        rospy.loginfo(f"Received /move_to_place command: {place}")

        if place == 1:
            self.task_place_1()
        elif place == 2:
            self.task_place_2()
        elif place == 3:
            self.task_place_3()
        else:
            rospy.logwarn(f"Unknown place command: {place}")

# ------------- MAIN -------------
if _name_ == "_main_":
    try:
        node = MoveRobot()
        rospy.spin()  # wait for /move_to_place commands
    except rospy.ROSInterruptException:
        pass