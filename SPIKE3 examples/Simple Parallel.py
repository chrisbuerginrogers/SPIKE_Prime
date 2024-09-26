import runloop
import motor
from hub import port
from hub import light_matrix

p1,p2 = port.C,port.F

async def motor_stack():
    degrees = 180
    speed = 1000
    await motor.run_for_degrees(p1, degrees, speed)
    await motor.run_for_degrees(p1, degrees, speed, stop = motor.SMART_COAST)
    await motor.run_for_degrees(p1, -1 * degrees, speed, stop = motor.SMART_BRAKE)
    
async def hub_pixel_stack():
    light_matrix.set_pixel(1,1, 100)
    await runloop.sleep_ms(20000)
    light_matrix.clear()
    await runloop.sleep_ms(10000)
    display_set_pixel(2,2, 100)
    
runloop.run(motor_stack(), hub_pixel_stack())
