import sys
import time
import math
import RPi.GPIO as GPIO
import math
sys.path.append('../galatae-api/')
from robot import Robot
import traceback

def get_pose_from_point(point):
  roll=math.atan(float(point[1])/point[0])*180/math.pi-3
  return point+[180,roll]

def probe_at_defined_speed(xy_coord,speed,r,min_stack_height):
  r.set_joint_speed(speed)
  r.linear_probe(get_pose_from_point(xy_coord+[min_stack_height]))

def go_above_sheet(xy_coord,speed,r):
  r.set_joint_speed(speed)
  r.go_to_pose(get_pose_from_point(xy_coord+[50]))

def place_sheet(r,default_speed,xy_coord,pump_pin,min_stack_height):
  GPIO.output(pump_pin,GPIO.LOW)
  go_above_sheet(xy_coord,default_speed,r)
  probe_at_defined_speed(xy_coord,default_speed,r,min_stack_height)
  stack_height=r.get_tool_pose()[2]
  print("stack_height:",r.get_tool_pose()[2])
  time.sleep(2)
  go_above_sheet(xy_coord,default_speed,r)
  return stack_height

def pick_sheet(r,default_speed,xy_coord,pump_pin,min_stack_height):
  go_above_sheet(xy_coord,default_speed,r)
  GPIO.output(pump_pin,GPIO.HIGH)
  probe_at_defined_speed(xy_coord,20,r,min_stack_height)
  time.sleep(1)
  go_above_sheet(xy_coord,default_speed,r)
  #time.sleep(0.5)

def pick_and_place_sheet(pick_coord,place_coord,r,default_speed,pump_pin,min_stack_height):
  pick_sheet(r,default_speed,pick_coord,pump_pin,min_stack_height)
  return place_sheet(r,default_speed,place_coord,pump_pin,min_stack_height)

def check_if_stack_height_is_ok(stack_height,min_stack_height):
  return 1<stack_height-min_stack_height

def move_one_sheet_per_stack(stacks_coord,r,default_speed,pump_pin,stack_height,min_stack_height):
  i=0
  while i<len(stacks_coord) and check_if_stack_height_is_ok(stack_height,min_stack_height):
    previous_stack_height=stack_height
    stack_height=pick_and_place_sheet(stacks_coord[i][0],stacks_coord[i][1],r,default_speed,pump_pin,min_stack_height)
    if 1<abs(stack_height-previous_stack_height):
      #print("problem: stack_height=",stack_height,"but previous_stack_height=",previous_stack_height)
      stack_height=min_stack_height
    i+=1
  return stack_height
    
def main():
  r=Robot(False)
  pump_pin=5
  default_speed=50
  
  x_start=200+10
  #y_start=5
  delta_x=220+15
  delta_y=150+10
  number_of_stacks=3
  min_stack_height=-110

  GPIO.setmode(GPIO.BCM)
  GPIO.setup(pump_pin,GPIO.OUT)
  GPIO.output(pump_pin,GPIO.LOW)
  
  r.reset_and_home_joints()

  stacks_coord=[]
  first_line_N=min(number_of_stacks,3)
  for i in range(first_line_N):
    stacks_coord+=[[[x_start+delta_x,5+((1-first_line_N)/2+i)*delta_y],[x_start,0]]]
  
  print(stacks_coord)
  """
  if(3<number_of_stacks):
    for i in range(number_of_stacks-3):
      stacks_coord+=[[x_start,(2*j-1)*delta_y],[x_start,0]]
  """

  try:
    t=time.time()
    stack_height=pick_and_place_sheet(stacks_coord[0][0],stacks_coord[0][1],r,default_speed,pump_pin,min_stack_height)
    stack_height=move_one_sheet_per_stack(stacks_coord[1:],r,default_speed,pump_pin,stack_height,min_stack_height)
    print("t:",(time.time()-t)/number_of_stacks)
                                        
    while(check_if_stack_height_is_ok(stack_height,min_stack_height)):
      t=time.time()
      stack_height=move_one_sheet_per_stack(stacks_coord,r,default_speed,pump_pin,stack_height,min_stack_height)
      print("t:",(time.time()-t)/number_of_stacks)

  except:
    print(traceback.format_exc())

  GPIO.output(pump_pin,GPIO.LOW)
  r.set_joint_speed(default_speed)
  r.go_to_foetus_pos()
  r.disable_motors()

if __name__ == "__main__":
  main()