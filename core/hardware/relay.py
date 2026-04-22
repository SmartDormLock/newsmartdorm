import lgpio
import time
from config.settings import RELAY_PIN, DOOR_OPEN_TIME

# buka handle gpiochip
h = lgpio.gpiochip_open(0)

# set pin output
lgpio.gpio_claim_output(h, RELAY_PIN)

def open_door():
    print("?? Membuka pintu...")
    
    lgpio.gpio_write(h, RELAY_PIN, 1)  # ON
    time.sleep(DOOR_OPEN_TIME)
    
    lgpio.gpio_write(h, RELAY_PIN, 0)  # OFF
    
    print("?? Pintu terkunci kembali")
