# 🎲 D20DX

**D20DX** is a standalone dice rolling device powered by a Raspberry Pi Pico. It supports multiple dice types, coin flips, and critical roll feedback — all with physical controls and audio-visual feedback.

---

## ✨ Features

- Selectable dice types: d4, d6, d8, d10, d12, d20, d100
- Configurable number of dice (1–9)
- Coin flip mode with distinct chimes for HEAD or TAIL
- Audio feedback via passive speaker
- Critical roll detection with flashing + tone
- Adjustable display and LED brightness
- Adjustable sound volume: MUTE / LOW / HIGH
- Idle dimming and animated boot sequence
- Entropy pool-based random seed generation

---

## 🧰 Hardware Used

- Raspberry Pi Pico
- TM1637 4-digit 7-segment display
- 2x 10k potentiometers
- Analog joystick (X-axis + button used)
- Passive speaker
- Status LED (PWM controlled)
- 3x pushbuttons (Volume, Brightness, Mode Toggle)
- TP4056 charging board + 18650 battery

---

## 🔌 Pin Mapping

| Function          | GPIO | Notes                          |
|-------------------|------|--------------------------------|
| Display CLK       | GP0  | TM1637                         |
| Display DIO       | GP1  | TM1637                         |
| Joystick Button   | GP2  | Coin flip trigger              |
| Volume Button     | GP5  | Cycle MUTE / LO / HI           |
| Brightness Button | GP4  | Adjust brightness              |
| Status LED        | GP6  | Red LED (PWM)                  |
| Speaker           | GP7  | Passive buzzer                 |
| Mode Button       | GP8  | Arbitrary mode toggle *(disabled)* |
| Pot 1 (Die type)  | GP26 | ADC0                           |
| Pot 2 (Die count) | GP27 | ADC1                           |
| Joystick X-axis   | GP28 | ADC2                           |

---

## ⚙️ Setup & Usage

1. Flash the Pico with MicroPython
2. Upload `main.py` and any required libraries (e.g. `tm1637.py`)
3. Power via USB or TP4056 module + battery
4. Use potentiometers to select dice type and count
5. Flick the joystick to roll dice
6. Press joystick button to flip a coin
7. Use buttons to adjust volume and brightness

---

## 🎶 Sound Behavior

- 🎵 **Startup jingle** follows animated boot sequence
- 🔊 **Critical rolls**: rising/falling tone + display flash
- 🪙 **Coin flip**: ascending chime for HEAD, descending chime for TAIL
- 🎚 **Volume control**:
  - `MUTE`: Center bars only
  - `LO`: Displays `LO`
  - `HI`: Displays `HI`

---

## 🚧 Planned / Optional

- Arbitrary mode for d3–d100 (toggleable, currently disabled)
- External ADC support (e.g. ADS7830)
- Roll history recall button
- Visual indicator for current mode
- Printable case and PCB files

---

## 📷 Project Photos / Demo

tktktktk

---

## 📄 License

tktktktk