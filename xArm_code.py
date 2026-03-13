#!/usr/bin/env python
import sys
import time
import math
import rospy
from xarm_msgs.srv import *
from std_msgs.msg import Int32

import queue
import datetime
import random
import traceback
import threading
from xarm import version
from xarm.wrapper import XArmAPI


class RobotMain(object):
    """Robot Main Class"""
    def _init_(self, robot, **kwargs):
        self.alive = True
        self._arm = robot
        self._tcp_speed = 100
        self._tcp_acc = 2000
        self._angle_speed = 20
        self._angle_acc = 500
        self._vars = {}
        self._funcs = {}
        self._robot_init()

    # Robot init
    def _robot_init(self):
        self._arm.clean_warn()
        self._arm.clean_error()
        self._arm.motion_enable(True)
        self._arm.set_mode(0)
        self._arm.set_state(0)
        time.sleep(1)
        self._arm.register_error_warn_changed_callback(self._error_warn_changed_callback)
        self._arm.register_state_changed_callback(self._state_changed_callback)
        if hasattr(self._arm, 'register_count_changed_callback'):
            self._arm.register_count_changed_callback(self._count_changed_callback)

    def _error_warn_changed_callback(self, data):
        if data and data['error_code'] != 0:
            self.alive = False
            self.pprint('err={}, quit'.format(data['error_code']))
            self._arm.release_error_warn_changed_callback(self._error_warn_changed_callback)

    def _state_changed_callback(self, data):
        if data and data['state'] == 4:
            self.alive = False
            self.pprint('state=4, quit')
            self._arm.release_state_changed_callback(self._state_changed_callback)

    def _count_changed_callback(self, data):
        if self.is_alive:
            self.pprint('counter val: {}'.format(data['count']))

    def _check_code(self, code, label):
        if not self.is_alive or code != 0:
            self.alive = False
            ret1 = self._arm.get_state()
            ret2 = self._arm.get_err_warn_code()
            self.pprint(
                '{}, code={}, connected={}, state={}, error={}, ret1={}. ret2={}'.format(
                    label, code, self._arm.connected, self._arm.state, self._arm.error_code, ret1, ret2
                )
            )
        return self.is_alive

    @staticmethod
    def pprint(*args, **kwargs):
        try:
            stack_tuple = traceback.extract_stack(limit=2)[0]
            print('[{}][{}] {}'.format(
                time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())),
                stack_tuple[1],
                ' '.join(map(str, args))
            ))
        except:
            print(*args, **kwargs)

    @property
    def arm(self):
        return self._arm

    @property
    def is_alive(self):
        if self.alive and self._arm.connected and self._arm.error_code == 0:
            if self._arm.state == 5:
                cnt = 0
                while self._arm.state == 5 and cnt < 5:
                    cnt += 1
                    time.sleep(0.1)
            return self._arm.state < 4
        else:
            return False


# -------- TASK 1 (Pick) --------
class RobotMain1(RobotMain):
    def run(self):
        try:
            #code = self._arm.set_servo_angle(angle=[0, 0, 0, 0, 0], speed=self._angle_speed, mvacc=self._angle_acc, wait=True)
            #if not self._check_code(code, 'set_servo_angle'): return
            code = self._arm.set_position(*[206.8, 0.0, 670.5, 180, 0, 61.1], speed=self._tcp_speed, mvacc=self._tcp_acc, wait=True)
            if not self._check_code(code, 'set_position'): return
            code = self._arm.set_servo_angle(angle=[1.0, 24.6, -137.7, 113.0, -61.1],
                                             speed=self._angle_speed, mvacc=self._angle_acc, wait=True)
            if not self._check_code(code, 'set_servo_angle'): return
            time.sleep(2)
            code = self._arm.set_tgpio_digital(0, 1)
            if not self._check_code(code, 'set_tgpio_digital'): return
            time.sleep(2)
            code = self._arm.set_servo_angle(angle=[0.0, -55.8, -22.4, 78.2, -61.1],
                                             speed=self._angle_speed, mvacc=self._angle_acc, wait=True)
            if not self._check_code(code, 'set_servo_angle'): return
        except Exception as e:
            self.pprint('MainException: {}'.format(e))
        finally:
            self.alive = False


# -------- TASK 2 (Place) --------
class RobotMain2(RobotMain):
    def run(self):
        try:
            code = self._arm.set_position(*[221.9, 0.0, 608.4, 180, 0, 61.1], speed=self._tcp_speed, mvacc=self._tcp_acc, wait=True)
            if not self._check_code(code, 'set_position'): return
            code = self._arm.set_servo_angle(angle=[0.0, -4.0, -93.6, 97.6, -61.1],
                                             speed=self._angle_speed, mvacc=self._angle_acc, wait=True)
            if not self._check_code(code, 'set_servo_angle'): return
            time.sleep(2)
            code = self._arm.set_tgpio_digital(0, 0)
            if not self._check_code(code, 'set_tgpio_digital'): return
            time.sleep(2)
            code = self._arm.set_position(*[139.4, 0.0, 546.1, 180, 0, 61.1],
                                          speed=self._tcp_speed, mvacc=self._tcp_acc, wait=True)
            if not self._check_code(code, 'set_position'): return
        except Exception as e:
            self.pprint('MainException: {}'.format(e))
        finally:
            self.alive = False


def movexArm(task_id):
    """Execute pick or place motion and notify completion"""
    rospy.loginfo(f"Starting xArm task {task_id}")
    arm = XArmAPI('192.168.31.203', baud_checkset=False)
    if task_id == 1:
        robot_main = RobotMain1(arm)
    else:
        robot_main = RobotMain2(arm)

    robot_main.run()
    rospy.loginfo(f"xArm task {task_id} completed")

    # Notify state machine that xArm task is done
    pub_done = rospy.Publisher("/xarm_done", Int32, queue_size=10)
    time.sleep(1)  # ensure publisher registers
    pub_done.publish(task_id)
    rospy.loginfo(f"Published /xarm_done {task_id}")


def callback(msg):
    rospy.loginfo(f"Received signal on /prueba: {msg.data}")
    if msg.data in [1, 2]:
        movexArm(msg.data)


if _name_ == "_main_":
    rospy.init_node("xArm_controller")
    rospy.Subscriber("/prueba", Int32, callback)
    rospy.loginfo("xArm node ready, waiting for signal on /prueba...")
    rospy.spin()