#!/usr/bin/env python3
import pygame
import ptext
import os
import psutil
import socket
import time
import subprocess

# https://www.geeksforgeeks.org/python-display-text-to-pygame-window/
# https://raw.githubusercontent.com/giampaolo/psutil/master/scripts/ifconfig.py
# https://github.com/cosmologicon/pygame-text
# https://unix.stackexchange.com/questions/58961/how-do-i-let-an-sdl-app-not-running-as-root-use-the-console

os.putenv("SDL_FBDEV", "/dev/fb1")
pygame.init()
pygame.mouse.set_visible(False)


def ifconfig():
    af_map = {
        socket.AF_INET: "IP",
        psutil.AF_LINK: "MAC",
    }
    text = ""
    stats = psutil.net_if_stats()
    for nic, addrs in psutil.net_if_addrs().items():
        if nic != "lo":
            text += "\n%s is " % (nic)
            if nic in stats:
                st = stats[nic]
                text += "%s\n" % ("UP" if st.isup else "DOWN")
            for addr in addrs:
                if addr.family in af_map:
                    text += "%s: " % af_map.get(addr.family, addr.family)
                    if addr.netmask:
                        text += "%s/%s\n" % (addr.address, addr.netmask)
                    else:
                        text += "%s" % addr.address
            if nic == "wlan0":
                ssid = subprocess.check_output(
                    "iwgetid -r", shell=True, universal_newlines=True
                ).strip()
                text += "\nSSID: %s\n" % ssid
            #text += "\n"
    return text


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLUE = (0, 0, 128)
T_DELTA = 10
display_width = 480
display_height = 320

hostname = socket.gethostname()
lcd = pygame.display.set_mode((display_width, display_height))

logoImg = pygame.image.load('croc_logo.png')

while True:
    interfaces = ifconfig()
    # text = font.render(interfaces, True, GREEN, BLUE)
    lcd.fill(BLACK)
    ptext.draw("Hostname: " + hostname, (10, 10), fontsize=48, color=WHITE)
    ptext.draw(interfaces, (10, 40), color=GREEN)
    lcd.blit(logoImg, (display_width-100,0))
    # lcd.blit(text, (0,0))
    # lcd.blit(text, textRect)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
    pygame.display.update()
    time.sleep(T_DELTA)
