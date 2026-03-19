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
  return xy_coord+[z,180,90+20+roll]

def place_sheet(r,default_speed,xy_coord,h_above_sheets,pump_pin,probe_speed):
  r.set_joint_speed(default_speed)
  r.go_to_pose(get_pose_from_xy(xy_coord,h_above_sheets))
  r.set_joint_speed(probe_speed)
  r.linear_probe(get_pose_from_xy(xy_coord,-150))
  GPIO.output(pump_pin,GPIO.LOW)
  r.go_to_pose(get_pose_from_xy(xy_coord,h_above_sheets))

def pick_sheet(r,default_speed,xy_coord,h_above_sheets,pump_pin,probe_speed):
  r.set_joint_speed(default_speed)
  r.go_to_pose(get_pose_from_xy(xy_coord,h_above_sheets))
  GPIO.output(pump_pin,GPIO.HIGH)
  r.set_joint_speed(probe_speed)
  r.linear_probe(get_pose_from_xy(xy_coord,-150))
  time.sleep(1)
  r.linear_move_to_pose(get_pose_from_xy(xy_coord,h_above_sheets))

def pick_and_place_sheet(pick_coord,place_coord,r,default_speed,h_above_sheets,pump_pin,probe_speed):
  pick_sheet(r,default_speed,pick_coord,h_above_sheets,pump_pin,probe_speed)
  place_sheet(r,default_speed,place_coord,h_above_sheets,pump_pin,probe_speed)

def main():
  r=Robot(False)
  pump_pin=4
  default_speed=50
  probe_speed=20
  h_above_sheets=-50
  
  x_start=200
  delta_x=220+15
  delta_y=150+10
  number_of_piles=3
  sheets_per_pile=2

  GPIO.setmode(GPIO.BCM)
  GPIO.setup(pump_pin,GPIO.OUT)
  GPIO.output(pump_pin,GPIO.LOW)
  
  r.reset_and_home_joints()
  r.set_joint_speed(default_speed)

  try:
    for i in range(sheets_per_pile):
      t=time.time()
      for j in range(number_of_piles):
        pick_and_place_sheet([x_start+delta_x,((1-number_of_piles)/2+j)*delta_y],[x_start,0],r,default_speed,h_above_sheets,pump_pin,probe_speed)
      print("t:",time.time()-t)

  except:
    print("error:")

  GPIO.output(pump_pin,GPIO.LOW)
  r.set_joint_speed(default_speed)
  r.go_to_foetus_pos()
  r.disable_motors()

if __name__ == "__main__":
  main()