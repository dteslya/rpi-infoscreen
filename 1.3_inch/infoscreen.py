#!/usr/bin/env python3

from luma.core.interface.serial import spi
from luma.core.render import canvas

from luma.oled.device import sh1106
import RPi.GPIO as GPIO

import sys
import time
import subprocess

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

# GPIO define
RST_PIN = 25  # Reset
CS_PIN = 8
DC_PIN = 24
JS_U_PIN = 6  # Joystick Up
JS_D_PIN = 19  # Joystick Down
JS_L_PIN = 5  # Joystick Left
JS_R_PIN = 26  # Joystick Right
JS_P_PIN = 13  # Joystick Pressed
BTN1_PIN = 21
BTN2_PIN = 20
BTN3_PIN = 16

# Some constants
SCREEN_LINES = 4
SCREEN_SAVER = 20.0
CHAR_WIDTH = 19
font = ImageFont.load_default()
width = 128
height = 64
x0 = 0
x1 = 84
y0 = -2
y1 = 12
x2 = x1 + 7
x3 = x1 + 14
x4 = x1 + 9
x5 = x2 + 9
x6 = x3 + 9


# init GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(JS_U_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up
GPIO.setup(JS_D_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up
GPIO.setup(JS_L_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up
GPIO.setup(JS_R_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up
GPIO.setup(JS_P_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up
GPIO.setup(BTN1_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up
GPIO.setup(BTN2_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up
GPIO.setup(BTN3_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Input with pull-up

# Initialize the display...
serial = spi(
    device=0,
    port=0,
    bus_speed_hz=8000000,
    transfer_size=4096,
    gpio_DC=DC_PIN,
    gpio_RST=RST_PIN,
)
device = sh1106(serial, rotate=2)  # sh1106
draw = ImageDraw.Draw(Image.new("1", (width, height)))
draw.rectangle((0, 0, width, height), outline=0, fill=0)

state = 0  # System state: 0 - screen is off; equal to channel number (e.g. BTN2_PIN, JS_P_PIN) otherwise
horz = 1  # Selection choice: 0 - Right; 1 - Left
vert = 3  # Selection choice: 1 - Top; 2 - Middle; 3 - Bottom
stamp = time.time()  # Current timestamp
start = time.time()  # Start screen saver count down
iface = ""
idxWin = 0
idxLen = 0
aplist = []
apIndx = -1


def select_h(channel):
    global apIndx
    global start
    global pwdLen
    global horz
    global vert
    if channel == JS_L_PIN:
        start = time.time()
        horz = 1
        draw_scn(state)
    elif channel == JS_R_PIN:
        start = time.time()
        horz = 0
        draw_scn(state)
    else:
        pass


def select_v(channel):
    global idxWin
    global start
    global vert
    if vert > 3:
        vert = 3
    if channel == JS_U_PIN:
        start = time.time()
        if vert > 1:
            vert = vert - 1
    elif channel == JS_D_PIN:
        start = time.time()
        if vert < 3:
            vert = vert + 1
    else:
        pass


def draw_scn(channel):
    global idxLen
    global pwdLen
    global apIndx
    with canvas(device) as draw:
        LINE0 = subprocess.check_output("hostname", shell=True)
        LINE1 = ""
        LINE2 = ""
        LINE3 = ""
        LINE4 = ""
        if channel == BTN1_PIN:
            if horz == 1:
                ssid = subprocess.check_output(
                    "iwgetid --raw | awk '{printf \"WiFi:%s\", $0}'", shell=True
                )
                freq = subprocess.check_output(
                    'iwgetid --freq | awk \'{gsub(/Frequency:/,""); printf " %.1f %s", $2,$3}\'',
                    shell=True,
                )
                LINE1 = subprocess.check_output(
                    "hostname -I | awk '{printf \"IP: %s\", $1}'", shell=True
                )
                LINE2 = subprocess.check_output(
                    'df -h / | awk \'$NF=="/"{printf "Disk:%s/%s %s", $3,$2,$5}\'',
                    shell=True,
                )
                LINE3 = ssid + freq
                LINE4 = subprocess.check_output(
                    "cat /sys/class/thermal/thermal_zone0/temp | awk '{printf \"Temp:%.1fC\", $1/1000}'",
                    shell=True,
                )
                draw.rectangle((0, 61, 84, 63), outline=255, fill=1)
                draw.rectangle((85, 61, 127, 63), outline=255, fill=0)
            else:
                LINE1 = subprocess.check_output(
                    "top -bn1 | awk 'NR==3{printf \"CPU:%.1f%% idle\", $8}'", shell=True
                )
                LINE2 = subprocess.check_output(
                    "free -mh | awk 'NR==2{printf \"Mem:%s/%s %.1f%%\", $3,$2,$3*100/$2 }'",
                    shell=True,
                )
                LINE3 = "  in Kbps  out Kbps"
                LINE4 = subprocess.check_output(
                    "ifstat -bT 0.1 1 | awk 'NR==3{printf \"%9.2f %9.2f\",$3,$4}'",
                    shell=True,
                )
                draw.rectangle((0, 61, 42, 63), outline=255, fill=0)
                draw.rectangle((43, 61, 127, 63), outline=255, fill=1)
        elif channel == BTN2_PIN:
            # Operating mode
            LINE1 = subprocess.check_output(
                'qmicli -d /dev/cdc-wdm0 --dms-get-operating-mode | awk \'/Mode: /{gsub("\\047",""); printf "Status: %s", $NF}\'',
                shell=True,
            )
            # Network name
            LINE2 = subprocess.check_output(
                'qmicli -d /dev/cdc-wdm0 --nas-get-home-network | awk \'/Description: /{gsub("\\047",""); printf "Network: %s", $NF}\'',
                shell=True,
            )
            # Signal strength
            LINE3 = subprocess.check_output(
                'qmicli -d /dev/cdc-wdm0 --nas-get-signal-strength | awk \'/RSSI/{getline;gsub("\\047","");printf "RSSI: %s dBm", $3}\'',
                shell=True,
            )
        else:
            pass

        draw.text((x0, y0), LINE0, font=font, fill=255)
        if len(LINE1) > CHAR_WIDTH:
            draw.text((x0, y1), LINE1[:CHAR_WIDTH], font=font, fill=255)
        else:
            draw.text((x0, y1), LINE1, font=font, fill=255)

        if len(LINE2) > CHAR_WIDTH:
            draw.text((x0, y1 * 2), LINE2[:CHAR_WIDTH], font=font, fill=255)
        else:
            draw.text((x0, y1 * 2), LINE2, font=font, fill=255)

        if len(LINE3) > CHAR_WIDTH:
            draw.text((x0, y1 * 3), LINE3[:CHAR_WIDTH], font=font, fill=255)
        else:
            draw.text((x0, y1 * 3), LINE3, font=font, fill=255)

        if len(LINE4) > CHAR_WIDTH:
            draw.text((x0, y1 * 4), LINE4[:CHAR_WIDTH], font=font, fill=255)
        else:
            draw.text((x0, y1 * 4), LINE4, font=font, fill=255)


def main_fun(channel):
    global serial
    global device
    global draw
    global state
    global start
    global apIndx
    if state <= 0:  # Display is off
        if channel > 0:  # A button is pressed, turn on display
            # Initialize the display...
            serial = spi(
                device=0,
                port=0,
                bus_speed_hz=8000000,
                transfer_size=4096,
                gpio_DC=DC_PIN,
                gpio_RST=RST_PIN,
            )
            device = sh1106(serial, rotate=2)  # sh1106
            image = Image.new("1", (width, height))
            draw = ImageDraw.Draw(image)
            draw.rectangle((0, 0, width, height), outline=0, fill=0)

            state = channel
            start = time.time()
            apIndx = -1
            draw_scn(channel)
        else:
            pass
    else:  # Display is on
        if (
            (channel > 0)
            and (channel == state)
            and ((channel != BTN2_PIN) or (apIndx < 0))
        ) or (
            (stamp - start) > SCREEN_SAVER
        ):  # A button is pressed or timed out, turn off display
            GPIO.output(RST_PIN, GPIO.LOW)
            state = 0
            apIndx = -1
        elif (
            (channel > 0)
            and (channel != state)
            and ((state != BTN2_PIN) or (apIndx < 0) or (channel == 998))
        ):
            state = channel
            start = time.time()
            draw_scn(channel)
        else:  # state > 0 && channel == 0 && not-yet-timeout, refresh screen
            draw_scn(state)


GPIO.add_event_detect(BTN1_PIN, GPIO.RISING, callback=main_fun, bouncetime=200)
GPIO.add_event_detect(BTN2_PIN, GPIO.RISING, callback=main_fun, bouncetime=200)
GPIO.add_event_detect(BTN3_PIN, GPIO.RISING, callback=main_fun, bouncetime=200)
GPIO.add_event_detect(JS_L_PIN, GPIO.RISING, callback=select_h, bouncetime=200)
GPIO.add_event_detect(JS_R_PIN, GPIO.RISING, callback=select_h, bouncetime=200)
GPIO.add_event_detect(JS_U_PIN, GPIO.RISING, callback=select_v, bouncetime=200)
GPIO.add_event_detect(JS_D_PIN, GPIO.RISING, callback=select_v, bouncetime=200)

iface = subprocess.check_output("iwgetid | awk '{print $1}'", shell=True).rstrip(
    b"\r\n"
)

# Main Loop
try:
    main_fun(BTN1_PIN)
    while True:
        stamp = time.time()
        main_fun(0)
        time.sleep(1)

except:
    print("Stopped", sys.exc_info()[0])
    GPIO.cleanup()
    raise
