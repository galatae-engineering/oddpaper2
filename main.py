import sys
import time
import math
import RPi.GPIO as GPIO
import math
sys.path.append('../galatae-api/')
from robot import Robot

def go_to_pose_at_specific_height(pose,height,r):
    pose[2]=height
    r.go_to_pose(pose)

def get_pose_from_xy(xy_coord,z):
  roll=math.atan(float(xy_coord[1])/xy_coord[0])*180/math.pi
  print(roll)
  return xy_coord+[z,180,90+roll]

def place_sheet(r,default_speed,xy_coord,h_above_sheets,pump_pin):
  r.set_joint_speed(default_speed)
  r.go_to_pose(get_pose_from_xy(xy_coord,h_above_sheets))
  r.set_joint_speed(5)
  r.linear_probe(get_pose_from_xy(xy_coord,-150))
  GPIO.output(pump_pin,GPIO.LOW)
  r.go_to_pose(get_pose_from_xy(xy_coord,h_above_sheets))

def pick_sheet(r,default_speed,xy_coord,h_above_sheets,pump_pin):
  r.set_joint_speed(default_speed)
  r.go_to_pose(get_pose_from_xy(xy_coord,h_above_sheets))
  GPIO.output(pump_pin,GPIO.HIGH)
  r.set_joint_speed(5)
  r.linear_probe(get_pose_from_xy(xy_coord,-150))
  print(r.get_tool_pose())
  time.sleep(1)
  r.linear_move_to_pose(get_pose_from_xy(xy_coord,h_above_sheets))

def pick_and_place_sheet(pick_coord,place_coord,r,default_speed,h_above_sheets,pump_pin):
  pick_sheet(r,default_speed,pick_coord,h_above_sheets,pump_pin)
  place_sheet(r,default_speed,place_coord,h_above_sheets,pump_pin)

def main():
  r=Robot(False)
  pump_pin=4
  default_speed=30
  h_above_sheets=-50

  x_start=200
  dx=220
  dy=150

  GPIO.setmode(GPIO.BCM)
  GPIO.setup(pump_pin,GPIO.OUT)
  GPIO.output(pump_pin,GPIO.LOW)
  
  r.reset_and_home_joints()
  #r.reset_and_home_joints()
  r.set_joint_speed(default_speed)

  pick_and_place_sheet([x_start+dx+15,-dy-10],[x_start,0],r,default_speed,h_above_sheets,pump_pin)
  pick_and_place_sheet([x_start+dx+15,0],[x_start,0],r,default_speed,h_above_sheets,pump_pin)
  pick_and_place_sheet([x_start+dx+15,dy+10],[x_start,0],r,default_speed,h_above_sheets,pump_pin)
  
  #pick_sheet(r,default_speed,[250,0],h_above_sheets,pump_pin)
  #place_sheet(r,default_speed,[450,0],h_above_sheets,pump_pin)
  GPIO.output(pump_pin,GPIO.LOW)
  r.set_joint_speed(default_speed)
  r.go_to_foetus_pos()
  GPIO.output(pump_pin,GPIO.LOW)
  r.disable_motors()

if __name__ == "__main__":
  main()