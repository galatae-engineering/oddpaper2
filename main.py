import sys
import time
import math
import RPi.GPIO as GPIO
import math
sys.path.append('../galatae-api/')
from robot import Robot
import traceback

"""
def get_pose_from_point(point):
  roll=math.atan(float(point[1])/point[0])*180/math.pi-3
  return point+[180,roll]
  def go_above_sheet(r,speed,xy_coord,safe_height):
  r.set_joint_speed(speed)
  r.go_to_pose(get_pose_from_point(xy_coord+[safe_height]))

"""
def probe_at_defined_speed(r,speed,xy_coord,roll):
  r.set_joint_speed(speed)
  r.linear_probe(xy_coord+[-110,180,roll])

def go_at_defined_speed(r,speed,xy_coord,z,roll):
  r.set_joint_speed(speed)
  r.go_to_pose(xy_coord+[z,180,roll])

def place_sheet(pump_pin,r,default_speed,xy_coord,safe_height,roll,sensor_pin):
  GPIO.output(pump_pin,GPIO.LOW)
  go_at_defined_speed(r,default_speed,xy_coord,safe_height,roll)
  probe_at_defined_speed(r,default_speed,xy_coord,roll)
  print("stack_height:",r.get_tool_pose()[2])

  r.jog([0,0,50,0,0])
  dt=0.1
  i=0
  success=GPIO.input(sensor_pin)
  while(not success and i*dt<10):
    time.sleep(0.1)
    i+=1
    success=GPIO.input(sensor_pin)

  go_at_defined_speed(r,default_speed,xy_coord,safe_height,roll)
  return success

def pick_sheet(r,default_speed,xy_coord,safe_height,roll,pump_pin,sensor_pin):
  go_at_defined_speed(r,default_speed,xy_coord,safe_height,roll)
  GPIO.output(pump_pin,GPIO.HIGH)

  number_of_trials=0
  success=False
  while(not success and number_of_trials<3):
    probe_at_defined_speed(r,20,xy_coord,roll)
    time.sleep(number_of_trials)
    r.jog([0,0,100,0,0])
    success=not GPIO.input(sensor_pin)
    number_of_trials+=1
  
  go_at_defined_speed(r,default_speed,xy_coord,safe_height,roll)

  return success

def pick_and_place_sheet(r,default_speed,pick_xy_roll,pump_pin,sensor_pin,place_xy_roll):
  safe_height=50
  success=pick_sheet(r,default_speed,pick_xy_roll[0:2],safe_height,pick_xy_roll[2],pump_pin,sensor_pin)
  
  if(success):
    success=place_sheet(pump_pin,r,default_speed,place_xy_roll[0:2],safe_height,place_xy_roll[2],sensor_pin)

  return success

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
  number_of_stacks=5

  stacks_xy_roll=[]
  first_line_N=min(number_of_stacks,3)
  for i in range(first_line_N):
    x=x_start+delta_x
    y=5+((1-first_line_N)/2+i)*delta_y
    stacks_xy_roll+=[[x,y,get_roll(x,y)]]
  
  if(3<number_of_stacks):
    for i in range(number_of_stacks-3):
      x=x_start
      y=(2*i-1)*delta_y
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

  r.reset_and_home_joints()

  try:
    t=time.time()
    go_on=pick_and_place_sheet(r,default_speed,stacks_xy_roll[0],pump_pin,sensor_pin,[x_start,0,0])
    if(go_on):
      go_on=move_one_sheet_per_stack(stacks_xy_roll[1:],r,default_speed,pump_pin,sensor_pin,x_start)
    print("t:",(time.time()-t)/len(stacks_xy_roll))
                                        
    while(go_on):
      t=time.time()
      go_on=move_one_sheet_per_stack(stacks_xy_roll,r,default_speed,pump_pin,sensor_pin,x_start)
      print("t:",(time.time()-t)/len(stacks_xy_roll))

  except:
    print(traceback.format_exc())

  GPIO.output(pump_pin,GPIO.LOW)
  r.set_joint_speed(default_speed)
  r.go_to_foetus_pos()
  r.disable_motors()

if __name__ == "__main__":
  main()