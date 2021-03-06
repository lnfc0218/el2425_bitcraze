#!/usr/bin/env python

import rospy
import math
import sys
import tf
from el2425_bitcraze.srv import SetTargetPosition 
from el2425_bitcraze.srv import SetPolygonTrajectory 
from geometry_msgs.msg import PoseStamped
from geometry_msgs.msg import Point

rate = 5
deltaTheta = 20

class PolygonTrajectoryPlanner:
    def __init__(self):
        self.rate = rospy.Rate(rate) # 3hz     

        self.goal = [0, 0, 0]
        
        rospy.Subscriber('goal', PoseStamped, self.cfGoalCallback)
        self.setTargetPosition = rospy.ServiceProxy('set_target_position', SetTargetPosition)

        rospy.Service('set_polygon_trajectory', SetPolygonTrajectory, self.polygonTrajectoryCallback)

        self.planTrajectory = False
        self.onCircle = False

    def polygonTrajectoryCallback(self, req): 
        self.center = req.center
        self.r = req.r
        self.xrotation = req.xrotation
        self.onCircle = False
        self.theta = 0

        if not self.planTrajectory:
            self.planTrajectory = True

        return()

    def run(self):
        self.theta = 0
        while not rospy.is_shutdown():
            if self.planTrajectory:
                if self.isOnCircle():
                    self.onCircle = True
                    theta_rad = math.pi*self.theta/180
                    x_new = self.center[0] + self.r*math.cos(theta_rad)
                    y_new = self.center[1] + self.r*math.sin(theta_rad)*math.cos(self.xrotation*math.pi/180)
                    z_new = self.center[2] - self.r*math.sin(theta_rad)*math.sin(self.xrotation*math.pi/180)

                    # step/ increment of 5 degrees.
                    # this step decides the shape of the cirlce
                    # if we change it to 90 degrees the tarjectory will become square
                    distToTarget = math.sqrt(math.pow(self.goal[0]-x_new,2) + math.pow(self.goal[1]-y_new,2) + math.pow(self.goal[2]-z_new,2)) 
                    if distToTarget <= 0.1:
                        self.theta = self.theta + deltaTheta       #10
                    #print "Point: %f" %(self.point.x)

                    if self.theta >= 360:
                        self.theta = 0
                else:
                    x_new = self.center[0] + self.r
                    y_new = self.center[1]
                    z_new = self.center[2]
                
                self.setTargetPosition(x_new, y_new, z_new)
            self.rate.sleep()

    def isOnCircle(self):
        if self.onCircle:
            return True
        else:
            x = self.goal[0]
            y = self.goal[1]
            z = self.goal[2]
            x0 = self.center[0] + self.r
            y0 = self.center[1]
            z0 = self.center[2]
            dist = math.sqrt(math.pow(x-x0,2) + math.pow(y-y0,2) + math.pow(z-z0,2)) 
            return dist <= 0.1

    def cfGoalCallback(self, goal):
        self.goal = [goal.pose.position.x, goal.pose.position.y, goal.pose.position.z]
            
if __name__ == "__main__":
    rospy.init_node("trajectory_handler")

    trajHandler = PolygonTrajectoryPlanner()
    trajHandler.run()
