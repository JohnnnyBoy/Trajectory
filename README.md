# Trajectory
Trajectory Code for collaborative robot B1 from Universal Robots Mexico.
Pick and place movement for cobot xArm of UFactory Mexico. 

## 📌 Introduction
There was a collaboration between the students of the Tecnológico de Monterrey and the companies Universal Studios and UFactory to build a automated and closed-loop assembly process for 3D-printed supportive springs. It was all part of the final challenge of Cyber Physical Systems I with the big company partner OMRON Robots. 
The objective was to use two different cobots for creating a whole assembly process with handover from rack to assembly station, conveyors, the other cobot and finally the rack.

## 💻 Challenge description
**First part (OMRON):**

The OMRON LD-60 mobile robot and TM5-700 collaborative arm where used for the first part of the process. Both units were connected to the TEC laboratory network. Using the Mobile Planner software for mapping, waypoint definition, and trajectory planning. 
For the camera based pick and place movement was used TMFlow, a visual pragramming environment. 

**Second part (Universal Studios, UFactory):**

The objective was to program and equip the mobile robot B1 to drive selfby for pick and place the prototype fixture to the goal rack with help of the xArm on top of the B1 robot. 

There were used ultrasonic and infrared camera sensors to detect obstacles for bypass. 
For most efficient movement there was used an error based cloesd-loop trajectory code for power saving turns in all directions. 
The whole code was written with Python 3 in ROS I. 
For right orientation in the laboratory there was used odometry with starting point as 0/0/0.

##
<img width="140" height="280" alt="Omron_Robot" src="https://github.com/user-attachments/assets/aa6ec3d0-5aae-428b-a887-bbbc6e2fd2d2" />
<img width="140" height="280" alt="B1-xarm_picture" src="https://github.com/user-attachments/assets/1244f9d9-0095-43e3-ba69-4a50de878c3c" />

## Explanation Respository
The [Connect xArm](https://github.com/JohnnnyBoy/Trajectory/blob/main/Connect%20xArm) and [Connect B1](https://github.com/JohnnnyBoy/Trajectory/blob/main/Connect%20B1) files are the instruction manual for connecting the xArm to the B1 and both to the TEC laboratory network.
In the other scripts are the files for the single components of the cobots.

## Research Gate
If you´re interested in this project you can got on my Research Gate account [Jonas Westphal](https://www.researchgate.net/publication/396885299_Collaborative_Robot_Integration_with_ROS_and_IoT_for_Smart_Factory_Automation_Cyber-Physical-Systems_Approach) there you can read the full technical report of this challenge. 

## 
<img width="1000" height="500" alt="curso-en-linea-gratis-tec-de-monterrey" src="https://github.com/user-attachments/assets/ae95b1e7-bb44-4390-a6d8-5d174b00ae97" />

