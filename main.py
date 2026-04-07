import sys
import time
import math
import RPi.GPIO as GPIO
import math
sys.path.append('../galatae-api/')
from robot import Robot
import traceback

def get_pose_from_point(point):
  roll=math.atan(float(point[1])/point[0])*180/math.pi
  return point+[180,roll]

def probe_at_defined_speed(xy_coord,speed,r):
  r.set_joint_speed(speed)
  r.linear_probe(get_pose_from_point(xy_coord+[-150]))

def go_above_sheet(xy_coord,speed,r):
  r.set_joint_speed(speed)
  r.go_to_pose(get_pose_from_point(xy_coord+[-10]))

def place_sheet(r,default_speed,xy_coord,pump_pin):
  GPIO.output(pump_pin,GPIO.LOW)
  go_above_sheet(xy_coord,default_speed,r)
  probe_at_defined_speed(xy_coord,default_speed,r)
  time.sleep(2)
  go_above_sheet(xy_coord,default_speed,r)

def pick_sheet(r,default_speed,xy_coord,pump_pin):
  go_above_sheet(xy_coord,default_speed,r)
  GPIO.output(pump_pin,GPIO.HIGH)
  probe_at_defined_speed(xy_coord,20,r)
  time.sleep(1)
  go_above_sheet(xy_coord,default_speed,r)
  #time.sleep(0.5)

def pick_and_place_sheet(pick_coord,place_coord,r,default_speed,pump_pin):
  pick_sheet(r,default_speed,pick_coord,pump_pin)
  place_sheet(r,default_speed,place_coord,pump_pin)

def main():
  r=Robot(False)
  pump_pin=5
  default_speed=50
  
  x_start=200
  delta_x=220+25
  delta_y=150+10
  number_of_piles=3

  GPIO.setmode(GPIO.BCM)
  GPIO.setup(pump_pin,GPIO.OUT)
  GPIO.output(pump_pin,GPIO.LOW)
  
  r.reset_and_home_joints()

  try:
    for i in range(10):
      t=time.time()

      first_line_N=min(number_of_piles,3)
      for j in range(first_line_N):
        pick_and_place_sheet([x_start+delta_x,((1-first_line_N)/2+j)*delta_y],[x_start,0],r,default_speed,pump_pin)
      if(3<number_of_piles):
        for j in range(number_of_piles-3):
          pick_and_place_sheet([x_start,(2*j-1)*delta_y],[x_start,0],r,default_speed,pump_pin)
          pass
      print("t:",time.time()-t)

  except:
    print(traceback.format_exc())

  GPIO.output(pump_pin,GPIO.LOW)
  r.set_joint_speed(default_speed)
  r.go_to_foetus_pos()
  r.disable_motors()

if __name__ == "__main__":
  main()