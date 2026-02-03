# Airpiece — Wiring Guide

## Pin Reference (Raspberry Pi 5 GPIO Header)

```
                    3V3 [1]  [2]  5V
          (SDA) GPIO 2 [3]  [4]  5V
         (SCL) GPIO 3 [5]  [6]  GND
               GPIO 4 [7]  [8]  GPIO 14 (TXD)
                  GND [9]  [10] GPIO 15 (RXD)
              GPIO 17 [11] [12] GPIO 18 (PCM_CLK)
              GPIO 27 [13] [14] GND
              GPIO 22 [15] [16] GPIO 23
                  3V3 [17] [18] GPIO 24
    (SPI_MOSI) GPIO10 [19] [20] GND
    (SPI_MISO) GPIO 9 [21] [22] GPIO 25
    (SPI_SCLK) GPIO11 [23] [24] GPIO 8
                  GND [25] [26] GPIO 7
              GPIO  0 [27] [28] GPIO 1
              GPIO  5 [29] [30] GND
              GPIO  6 [31] [32] GPIO 12
              GPIO 13 [33] [34] GND
              GPIO 19 [35] [36] GPIO 16
              GPIO 26 [37] [38] GPIO 20
                  GND [39] [40] GPIO 21
```

---

## 1. Pi Camera Module 3

**Connection:** Ribbon cable to the CSI port on the Pi 5.

- Open the CSI connector latch (the small black clip on the Pi board)
- Insert the ribbon cable with contacts facing the board (away from the latch)
- Close the latch

No GPIO pins used — dedicated camera interface.

---

## 2. INMP441 I2S MEMS Microphone

The INMP441 is a digital mic that uses I2S protocol over GPIO.

| INMP441 Pin | RPi 5 Pin | GPIO | Description |
|-------------|-----------|------|-------------|
| VDD | Pin 1 | 3V3 | Power (3.3V) |
| GND | Pin 6 | GND | Ground |
| SCK | Pin 12 | GPIO 18 | I2S bit clock (BCLK) |
| WS | Pin 35 | GPIO 19 | I2S word select (LRCLK) |
| SD | Pin 38 | GPIO 20 | I2S data in |
| L/R | Pin 6 | GND | Tie to GND for left channel |

**Breadboard layout:**
```
INMP441          Jumper Wire          RPi 5
┌──────┐                            ┌──────────┐
│ VDD  │──── red ──────────────────│ Pin 1  3V3│
│ GND  │──── black ────────────────│ Pin 6  GND│
│ SCK  │──── yellow ───────────────│ Pin 12 G18│
│ WS   │──── green ────────────────│ Pin 35 G19│
│ SD   │──── blue ─────────────────│ Pin 38 G20│
│ L/R  │──── black ────────────────│ Pin 6  GND│
└──────┘                            └──────────┘
```

**Enable I2S on the Pi:**
Add to `/boot/firmware/config.txt`:
```
dtoverlay=i2s-mmap
dtoverlay=googlevoicehat-soundcard
```
Then reboot.

---

## 3. NEO-6M GPS Module

The GPS module communicates over UART serial.

| NEO-6M Pin | RPi 5 Pin | GPIO | Description |
|------------|-----------|------|-------------|
| VCC | Pin 2 | 5V | Power (5V) |
| GND | Pin 14 | GND | Ground |
| TXD | Pin 10 | GPIO 15 (RXD) | GPS TX → Pi RX |
| RXD | Pin 8 | GPIO 14 (TXD) | Pi TX → GPS RX |

**Note:** GPS TXD connects to Pi RXD and vice versa (crossover).

```
NEO-6M           Jumper Wire          RPi 5
┌──────┐                            ┌──────────┐
│ VCC  │──── red ──────────────────│ Pin 2   5V│
│ GND  │──── black ────────────────│ Pin 14 GND│
│ TXD  │──── orange ──────────────│ Pin 10 RXD│
│ RXD  │──── yellow ──────────────│ Pin 8  TXD│
└──────┘                            └──────────┘
```

**Enable UART on the Pi:**
Add to `/boot/firmware/config.txt`:
```
enable_uart=1
dtoverlay=disable-bt
```
This disables Bluetooth on the built-in UART (we use WiFi Bluetooth instead) and frees up the primary UART for GPS.

---

## 4. Bluetooth Bone Conduction Earpiece

No wiring — pairs via Bluetooth.

**Pairing on the Pi:**
```bash
bluetoothctl
scan on
# Find your earpiece MAC address
pair XX:XX:XX:XX:XX:XX
connect XX:XX:XX:XX:XX:XX
trust XX:XX:XX:XX:XX:XX
```

Then set it as the default audio output:
```bash
pactl set-default-sink bluez_sink.XX_XX_XX_XX_XX_XX.a2dp_sink
```

---

## 5. Power (USB-C PD Power Bank)

- Plug USB-C PD power bank directly into Pi 5's USB-C power port
- That's it — the Pi 5 negotiates PD power automatically

---

## Complete Wiring Diagram

```
                              ┌──────────────────┐
                              │   Raspberry Pi 5  │
                              │                    │
    ┌──────────┐    ribbon    │  [CSI Port]        │
    │ Pi Cam 3 │──────────────│                    │
    └──────────┘              │                    │
                              │  Pin 1  (3V3) ────│──── INMP441 VDD
    ┌──────────┐              │  Pin 2  (5V)  ────│──── NEO-6M VCC
    │ INMP441  │              │  Pin 6  (GND) ────│──┬─ INMP441 GND
    │ I2S Mic  │              │  Pin 14 (GND) ────│──┤  INMP441 L/R
    └──────────┘              │                    │  └─ NEO-6M GND
                              │  Pin 8  (TXD) ────│──── NEO-6M RXD
    ┌──────────┐              │  Pin 10 (RXD) ────│──── NEO-6M TXD
    │ NEO-6M   │              │                    │
    │ GPS      │              │  Pin 12 (G18) ────│──── INMP441 SCK
    └──────────┘              │  Pin 35 (G19) ────│──── INMP441 WS
                              │  Pin 38 (G20) ────│──── INMP441 SD
    ┌──────────┐              │                    │
    │ BT       │ ~~ BT ~~~~~ │  [Bluetooth 5.0]   │
    │ Earpiece │              │                    │
    └──────────┘              │  [USB-C Power] ────│──── PD Power Bank
                              └──────────────────┘
```

## Checklist Before First Boot

- [ ] Camera ribbon seated firmly, latch closed
- [ ] Mic wired to correct I2S pins (check SCK/WS/SD)
- [ ] GPS TX → Pi RX, GPS RX → Pi TX (crossover correct)
- [ ] GPS antenna has clear view of sky (for fix)
- [ ] Power bank supports USB-C PD (5V/3A minimum)
- [ ] MicroSD card flashed with Raspberry Pi OS (64-bit)
- [ ] config.txt updated with I2S and UART overlays
- [ ] Bluetooth earpiece charged and in pairing mode
