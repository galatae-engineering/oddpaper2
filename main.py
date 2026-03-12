import sys
import time
import math
import RPi.GPIO as GPIO
sys.path.append('../galatae-api/')
from robot import Robot

def go_to_pose_at_specific_height(pose,height,r):
    pose[2]=height
    r.go_to_pose(pose)

def get_pose_from_xy(xy_coord,z):
  return xy_coord+[z,180,90]

def place_sheet(r,default_speed,xy_coord,h_above_sheets,pump_pin):
  r.set_joint_speed(default_speed)
  r.go_to_pose(get_pose_from_xy(xy_coord,h_above_sheets))
  r.set_joint_speed(5)
  r.linear_probe(get_pose_from_xy(xy_coord,-150))
  GPIO.output(pump_pin,GPIO.LOW)
  #r.set_joint_speed(default_speed)
  r.go_to_pose(get_pose_from_xy(xy_coord,h_above_sheets))

def pick_sheet(r,default_speed,xy_coord,h_above_sheets,pump_pin):
  r.set_joint_speed(default_speed)
  r.go_to_pose(get_pose_from_xy(xy_coord,h_above_sheets))
  GPIO.output(pump_pin,GPIO.HIGH)
  r.set_joint_speed(5)
  r.linear_probe(get_pose_from_xy(xy_coord,-150))
  r.jog([0,0,-20,0,0])
  print(r.get_tool_pose())
  time.sleep(1)
  #input()
  r.go_to_pose(get_pose_from_xy(xy_coord,h_above_sheets))

def main():
  r=Robot(False)
  pump_pin=4
  default_speed=30
  h_above_sheets=-80

  GPIO.setmode(GPIO.BCM)
  GPIO.setup(pump_pin,GPIO.OUT)
  GPIO.output(pump_pin,GPIO.LOW)
  
  r.reset_and_home_joints()
  #r.reset_and_home_joints()
  r.set_joint_speed(default_speed)
  r.reset_angles([-30,-80,155,0,0])

  pick_sheet(r,default_speed,[250,0],h_above_sheets,pump_pin)
  place_sheet(r,default_speed,[350,0],h_above_sheets,pump_pin)
  GPIO.output(pump_pin,GPIO.LOW)
  r.set_joint_speed(default_speed)
  r.go_to_foetus_pos()
  GPIO.output(pump_pin,GPIO.LOW)

if __name__ == "__main__":
  main()