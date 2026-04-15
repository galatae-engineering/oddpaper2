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

def get_all_stacks_xy_roll():
  x_start=200+10
  delta_x=220+15
  delta_y=150+10
  stacks_per_line=3

  xy_roll=[]
  for i in range(2):
    for j in range(stacks_per_line):
      x=x_start+i*delta_x
      y=5+((1-stacks_per_line)/2+j)*delta_y
      xy_roll+=[[x,y,get_roll(x,y)]]

  return xy_roll 

def delete_elements_from_list(indices,list_original):
  new_list=list_original.copy()
  sorted_indices=sorted(indices, reverse=True)
  for i in sorted_indices:
    del new_list[i]
  return new_list

def main():
  r=Robot(False)
  pump_pin=5
  sensor_pin=6  
  default_speed=50
  
  all_stacks_xy_rolls=get_all_stacks_xy_roll()
  place_stack_index=1
  separator_stack_index=5
  place_xy_roll=all_stacks_xy_rolls[place_stack_index]
  pick_xy_rolls=delete_elements_from_list([place_stack_index,separator_stack_index],all_stacks_xy_rolls)
  print(pick_xy_rolls)
  print(all_stacks_xy_rolls)
  

  GPIO.setmode(GPIO.BCM)
  GPIO.setup(sensor_pin,GPIO.IN)
  GPIO.setup(pump_pin,GPIO.OUT)
  GPIO.output(pump_pin,GPIO.LOW)

  go_on=True
  try:
    r.reset_and_home_joints()
    
    while go_on:
      t=time.time()
      page=0
      while(page<3 and go_on):
        random_index=random.randrange(0,len(pick_xy_rolls))
        go_on=pick_and_place_sheet(r,default_speed,pick_xy_rolls[random_index],pump_pin,sensor_pin,place_xy_roll)
        page+=1
      go_on=pick_and_place_sheet(r,default_speed,all_stacks_xy_rolls[separator_stack_index],pump_pin,sensor_pin,place_xy_roll)
      print("t:",(time.time()-t)/(len(pick_xy_rolls)+1))

  except:
    print(traceback.format_exc())

  GPIO.output(pump_pin,GPIO.LOW)
  r.set_joint_speed(default_speed)
  r.go_to_foetus_pos()
  r.disable_motors()

if __name__ == "__main__":
  main()