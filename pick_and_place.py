import RPi.GPIO as GPIO
import time
import math

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
  stack_height=r.get_tool_pose()[2]
  go_at_defined_speed(r,default_speed,xy_coord,max(safe_height,stack_height+50),roll)
 
  dt=0.1
  i=0
  sheet_dropped=GPIO.input(sensor_pin)
  print("sheet_dropped",sheet_dropped)
  while(not sheet_dropped and i*dt<10):
    time.sleep(0.1)
    i+=1
    sheet_dropped=GPIO.input(sensor_pin)

  print("sheet_dropped",sheet_dropped)

  """
  stack_full=20<stack_height
  if(stack_full):
    print("stack_height",stack_height)
  """

  return sheet_dropped #and not stack_full

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
  safe_height=35
  success=pick_sheet(r,default_speed,pick_xy_roll[0:2],safe_height,pick_xy_roll[2],pump_pin,sensor_pin)
  
  if(success):
    success=place_sheet(pump_pin,r,default_speed,place_xy_roll[0:2],safe_height,place_xy_roll[2],sensor_pin)

  return success