import sys
sys.path.append('../galatae-api/')
from robot import Robot
import traceback
import random
from pick_and_place import *

def move_one_sheet_per_stack(stacks_coord,r,default_speed,pump_pin,sensor_pin,x_start):
  i=0
  success=True
  while success and i<len(stacks_coord):
    success=pick_and_place_sheet(r,default_speed,stacks_coord[i],pump_pin,sensor_pin,[x_start,0,0])
    i+=1

  return success

def get_roll(x,y):
  return math.atan(float(y)/x)*180/math.pi-3

def get_stacks_xy_roll(x_start):
  delta_x=220+15
  delta_y=150+10
  stacks_per_line=3
  #number_of_stacks=9

  stacks_xy_roll=[]
  for i in range(2):
    for j in range(stacks_per_line):
      if(not(i==0 and j==(stacks_per_line-1)/2)):
        x=x_start+i*delta_x
        y=5+((1-stacks_per_line)/2+j)*delta_y
        stacks_xy_roll+=[[x,y,get_roll(x,y)]]

  return stacks_xy_roll 

def main():
  r=Robot(False)
  pump_pin=5
  sensor_pin=6  
  default_speed=50
  x_start=200+10
  stacks_xy_roll=get_stacks_xy_roll(x_start)
  print(stacks_xy_roll)

  GPIO.setmode(GPIO.BCM)
  GPIO.setup(sensor_pin,GPIO.IN)
  GPIO.setup(pump_pin,GPIO.OUT)
  GPIO.output(pump_pin,GPIO.LOW)

  go_on=True
  try:
    r.reset_and_home_joints()
    
    while(go_on):
      t=time.time()
      i=random.randrange(0,len(stacks_xy_roll))
      go_on=pick_and_place_sheet(r,default_speed,stacks_xy_roll[i],pump_pin,sensor_pin,[x_start,0,0])
      print("t:",(time.time()-t)/len(stacks_xy_roll))

  except:
    print(traceback.format_exc())

  GPIO.output(pump_pin,GPIO.LOW)
  r.set_joint_speed(default_speed)
  r.go_to_foetus_pos()
  r.disable_motors()

if __name__ == "__main__":
  main()