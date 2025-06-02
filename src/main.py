from machine import Pin, ADC, PWM, lightsleep
import tm1637
import urandom
import time

# --- Configurable Settings ---
FLICK_THRESHOLD = 10000
ROLL_DISPLAY_TIME = 10000
FLIP_DISPLAY_TIME = 5000
IDLE_TIMEOUT = 60000

# --- Volume Control (GP5) ---
volume_btn = Pin(5, Pin.IN, Pin.PULL_UP)
volume_levels = [0, 16384, 32768]
volume_labels = {
    0: [0x40, 0x40, 0x00, 0x00],
    1: [0x38, 0x3F, 0x00, 0x00],
    2: [0x76, 0x30, 0x00, 0x00],
}
volume_index = 2
last_volume_change = 0

# --- Brightness Control (GP4) ---
brightness_btn = Pin(4, Pin.IN, Pin.PULL_UP)
brightness_levels = [8192, 32768, 65535]
display_levels = [1, 4, 7]
brightness_index = 1
last_brightness_change = 0

# --- Mode Toggle Button (GP8) ---
mode_btn = Pin(8, Pin.IN, Pin.PULL_UP)
last_mode_toggle = 0
arbitrary_mode = False  # currently disabled

# --- Status LED (GP6) ---
status_led = PWM(Pin(6))
status_led.freq(1000)
def set_led(brightness):
    status_led.duty_u16(brightness)

# --- Passive Buzzer (GP7) ---
buzzer = PWM(Pin(7))
buzzer.freq(1000)
def play_tone(freq, duration_ms):
    buzzer.freq(freq)
    buzzer.duty_u16(volume_levels[volume_index])
    time.sleep_ms(duration_ms)
    buzzer.duty_u16(0)

# --- Display (TM1637) ---
tm = tm1637.TM1637(clk=Pin(0), dio=Pin(1))
tm.brightness(display_levels[brightness_index])

# --- Entropy Pool ---
entropy_pool = 0

# --- Boot Animation with Combined Startup Chime ---
def boot_animation():
    bar = 0x40
    progress_tones = [440, 523, 659, 784]
    roll_chime = [523, 659, 784]  # C5, E5, G5

    # Progress bar animation
    for i in range(4):
        digits = [0x00] * 4
        digits[i] = bar
        tm.write(digits)
        play_tone(progress_tones[i], 150)
        time.sleep(0.1)

    roll_text = [0x50, 0x3F, 0x38, 0x38]
    for i in range(3):
        tm.write(roll_text)
        play_tone(roll_chime[i], 150)
        time.sleep(0.3)
        tm.write([0, 0, 0, 0])
        time.sleep(0.2)

    tm.write([0, 0, 0, 0])

boot_animation()
time.sleep(0.5)

# --- ADC Setup ---
pot_type = ADC(26)
pot_count = ADC(27)
joystick_adc = ADC(28)

# --- Joystick Button (GP2) ---
joystick_btn = Pin(2, Pin.IN, Pin.PULL_UP)

# --- Constants ---
HEAD = [0x76, 0x79, 0x77, 0x5E]
TAIL = [0x78, 0x77, 0x30, 0x38]

flick_ready = True
last_flip_time = 0
dimmed = False
display_mode = "select"
last_activity_time = time.ticks_ms()
last_display_change = time.ticks_ms()
is_d100_mode = False  # Track if we're in d100 mode

# --- ADC Averaging ---
def read_average(adc, samples=4):
    return sum(adc.read_u16() for _ in range(samples)) // samples

def get_die_type():
    val = read_average(pot_type)
    options = [4, 6, 8, 10, 12, 20, 100]
    index = int((val / 65535) * len(options))
    return options[min(index, len(options) - 1)]

def get_dice_count():
    global is_d100_mode
    if is_d100_mode:
        return 1
    val = read_average(pot_count)
    count = int(((65535 - val) / 65535) * 9) + 1
    return min(count, 9)

def cycle_brightness():
    global brightness_index
    brightness_index = (brightness_index + 1) % len(brightness_levels)
    tm.brightness(display_levels[brightness_index])
    set_led(brightness_levels[brightness_index])

def cycle_volume():
    global volume_index
    volume_index = (volume_index + 1) % len(volume_levels)
    tm.write(volume_labels[volume_index])
    for freq in (659, 784, 880, 988):
        play_tone(freq, 80)
        time.sleep_ms(30)

def display_config(dice_count, die_type):
    digits = [0, 0, 0, 0]
    if die_type == 100:
        digits[0] = 0x5E
        digits[1] = tm.encode_digit(1)
        digits[2] = tm.encode_digit(0)
        digits[3] = tm.encode_digit(0)
    else:
        digits[0] = tm.encode_digit(dice_count)
        digits[1] = 0x5E
        if die_type < 10:
            digits[2] = tm.encode_digit(die_type)
            digits[3] = 0
        else:
            digits[2] = tm.encode_digit(die_type // 10)
            digits[3] = tm.encode_digit(die_type % 10)
    tm.write(digits)

def flash_result(result):
    for _ in range(2):
        tm.number(result)
        time.sleep(0.2)
        tm.write([0, 0, 0, 0])
        time.sleep(0.2)
    tm.number(result)

def rising_tone():
    for freq in (523, 587, 659, 784, 880, 988):
        play_tone(freq, 100)

def falling_tone():
    for freq in (988, 880, 784, 659, 587, 523):
        play_tone(freq, 100)

def rolling_animation(duration=1.5, interval=0.05):
    start = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), start) < duration * 1000:
        digits = ''.join(str(urandom.randint(0, 9)) for _ in range(4))
        tm.show(digits)
        set_led(urandom.getrandbits(16))
        time.sleep(interval)
    set_led(brightness_levels[brightness_index])

def coin_flip_chime(heads):
    tones = (880, 1047)
    if not heads:
        tones = reversed(tones)
    for freq in tones:
        play_tone(freq, 100)
        time.sleep_ms(30)

def coin_flip_animation(duration=1.0, interval=0.1):
    start = time.ticks_ms()
    symbols = [HEAD, TAIL]
    while time.ticks_diff(time.ticks_ms(), start) < duration * 1000:
        tm.write(symbols[urandom.getrandbits(1)])
        set_led(urandom.getrandbits(16))
        time.sleep(interval)
    set_led(brightness_levels[brightness_index])

def check_coin_flip():
    global last_flip_time, display_mode, last_display_change, dimmed
    now = time.ticks_ms()
    if joystick_btn.value() == 0 and time.ticks_diff(now, last_flip_time) > 500:
        last_flip_time = now
        coin_flip_animation()
        result = urandom.getrandbits(1)
        urandom.seed(entropy_pool ^ urandom.getrandbits(16))
        tm.write(HEAD if result == 0 else TAIL)
        coin_flip_chime(result == 0)
        display_mode = "flip"
        tm.brightness(display_levels[brightness_index])
        dimmed = False
        last_display_change = time.ticks_ms()

def is_flicked():
    global flick_ready
    x = joystick_adc.read_u16()
    deviation = abs(x - 32768)
    if joystick_btn.value() == 0:
        return False
    if deviation > FLICK_THRESHOLD and flick_ready:
        flick_ready = False
        return True
    elif deviation <= FLICK_THRESHOLD:
        flick_ready = True
    return False

def main():
    global last_activity_time, last_display_change, display_mode
    global dimmed, last_brightness_change, last_volume_change
    global entropy_pool, is_d100_mode

    prev_die_type = get_die_type()
    prev_dice_count = get_dice_count()

    while True:
        now = time.ticks_ms()

        entropy_pool ^= (time.ticks_ms() ^ joystick_adc.read_u16() ^ urandom.getrandbits(16))

        if brightness_btn.value() == 0 and time.ticks_diff(now, last_brightness_change) > 300:
            last_brightness_change = now
            cycle_brightness()

        if volume_btn.value() == 0 and time.ticks_diff(now, last_volume_change) > 300:
            last_volume_change = now
            cycle_volume()

        die_type = get_die_type()
        # Update d100 mode status
        is_d100_mode = (die_type == 100)
        dice_count = get_dice_count()

        if (die_type != prev_die_type or dice_count != prev_dice_count) and display_mode != "select":
            if time.ticks_diff(now, last_display_change) > 4000:
                display_mode = "select"
                tm.write([0, 0, 0, 0])
                tm.brightness(display_levels[brightness_index])
                dimmed = False

        if display_mode == "select":
            display_config(dice_count, die_type)
            set_led(brightness_levels[0] if dimmed else brightness_levels[brightness_index])

        if is_flicked():
            urandom.seed(entropy_pool ^ urandom.getrandbits(16))
            rolling_animation()
            total = sum(urandom.randint(1, die_type) for _ in range(dice_count))
            tm.number(total)

            if total == dice_count * die_type:
                flash_result(total)
                rising_tone()
            elif total == dice_count:
                flash_result(total)
                falling_tone()

            last_activity_time = now
            last_display_change = now
            display_mode = "roll"
            tm.brightness(display_levels[brightness_index])
            dimmed = False

        check_coin_flip()

        if display_mode == "roll" and time.ticks_diff(now, last_display_change) > ROLL_DISPLAY_TIME:
            display_mode = "select"
            tm.write([0, 0, 0, 0])

        if display_mode == "flip" and time.ticks_diff(now, last_display_change) > FLIP_DISPLAY_TIME:
            display_mode = "select"
            tm.write([0, 0, 0, 0])

        if time.ticks_diff(now, last_activity_time) > IDLE_TIMEOUT and not dimmed:
            tm.brightness(1)
            dimmed = True

        prev_die_type = die_type
        prev_dice_count = dice_count

        time.sleep(0.05)

main()
