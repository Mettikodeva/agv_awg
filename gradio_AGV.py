import gradio as gr
import utils
import serial
import time
import threading

client = serial.Serial(
    port='/dev/ttyUSB0',
    baudrate = 115200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
)

mode = "velocity"

line_follow = 0

def up():
    utils.send_to_motor(1, -25, mode, client)
    utils.send_to_motor(2, 25, mode, client)
    print("Robot should be moved")
    return "Forward"

def down():
    utils.send_to_motor(1, 25, mode, client)
    utils.send_to_motor(2, -25, mode, client)
    print("Robot should be moved")
    return "Backward"

def left_up():
    utils.send_to_motor(1, -25, mode, client)
    utils.send_to_motor(2, 0, mode, client)
    print("Robot should be moved")
    return "Left"

def right_up():
    utils.send_to_motor(1, 0, mode, client)
    utils.send_to_motor(2, 25, mode, client)
    print("Robot should be moved")
    return "Right"

def left_down():
    utils.send_to_motor(1, 25, mode, client)
    utils.send_to_motor(2, 0, mode, client)
    print("Robot should be moved")
    return "Left"

def right_down():
    utils.send_to_motor(1, 0, mode, client)
    utils.send_to_motor(2, -25, mode, client)
    print("Robot should be moved")
    return "Right"

def right_curve():
    utils.send_to_motor(1, -25, mode, client)
    utils.send_to_motor(2, -25, mode, client)
    print("Robot should be moved")
    return "Right"

def left_curve():
    utils.send_to_motor(1, 25, mode, client)
    utils.send_to_motor(2, 25, mode, client)
    print("Robot should be moved")
    return "Left"

def stop():
    global line_follow
    if line_follow == 1:
        line_follow = 0
        time.sleep(0.5)
    utils.send_to_motor(1, 0, mode, client)
    utils.send_to_motor(2, 0, mode, client)
    print("Robot should stop here")
    return "Stop"


def line():
    global line_follow
    
    set_point = 8.5
    basespeed = 25
    maxspeed = 35
    kp, ki, kd = 0.95, 0, 0

    temp_sensor = 8.5
    last_error = 0
    line_follow = 1
    i=0

    last_output = None
    second_output = None
    third_output = None
    fourth_output = None
    fifth_output = None
    
    v = 8.5

    while line_follow == 1:
        out = client.read(1)

        fifth_output = fourth_output
        fourth_output = third_output
        third_output = second_output
        second_output = last_output
        last_output = out

        if third_output == b'\x04' and fourth_output == b'\x03' and fifth_output == b'\x03':
            v = int.from_bytes(second_output+last_output, byteorder='big')

        current_point = utils.conversion_magnetic(v)
        print(f"temp : {temp_sensor} || curr : {current_point}")
        if  current_point == None:
            current_point = temp_sensor
        error = set_point-current_point
        p = error
        i = i + error 
        d = error - last_error
        last_error = error
        motorspeed = p*kp + i*ki + d*kd
        motor_speed_1 = basespeed + motorspeed
        motor_speed_2 = basespeed - motorspeed
        if motor_speed_1 > maxspeed:
            motor_speed_1 = maxspeed
        elif motor_speed_2 > maxspeed:
            motor_speed_2 = maxspeed
        elif motor_speed_1 < 0:
            motor_speed_1 = 0
        elif motor_speed_2 < 0:
            motor_speed_2 = 0
        print(motor_speed_1, motor_speed_2)
        utils.send_to_motor(1, -(int(motor_speed_2)), mode, client)
        utils.send_to_motor(2, int(motor_speed_1), mode, client)
        temp_sensor = current_point



with gr.Blocks() as demo:
    direction_text = gr.Textbox(label="Robot Direction")

    with gr.Column():
        with gr.Row():
            button_left_up = gr.Button(value="↖️")
            button_up = gr.Button(value="⬆️")
            button_right_up = gr.Button(value="↗️")
        with gr.Row():
            button_left_curve = gr.Button(value="↩️")
            button_stop = gr.Button(value="🛑")
            button_right_curve = gr.Button(value="↪️")
        with gr.Row():
            button_left_down = gr.Button(value="↙️")
            button_down = gr.Button(value="⬇️")
            button_right_down = gr.Button(value="↘️")

    line_follow = gr.Button(value="Line Follower")

    button_up.click(up, outputs=[direction_text])
    button_down.click(down, outputs=[direction_text])
    button_left_up.click(left_up, outputs=[direction_text])
    button_right_up.click(right_up, outputs=[direction_text])
    button_left_down.click(left_down, outputs=[direction_text])
    button_right_down.click(right_down, outputs=[direction_text])
    button_left_curve.click(left_curve, outputs=[direction_text])
    button_right_curve.click(right_curve, outputs=[direction_text])
    button_stop.click(stop, outputs=[direction_text])
    line_follow.click(line, outputs=[direction_text])


if __name__=="__main__":
  try:
    demo.launch(share=True)
  except KeyboardInterrupt:
    demo.clear()
    demo.close()
  except Exception as e:
    demo.clear()
    demo.close()