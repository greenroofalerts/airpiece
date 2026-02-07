# Airpiece — Bill of Materials

## Core Components

| # | Component | Spec | Approx Price | Where to Buy |
|---|-----------|------|-------------|--------------|
| 1 | **Raspberry Pi 5 (4GB)** | Quad-core ARM Cortex-A76, 4GB RAM, WiFi, BT 5.0 | £58 | [The Pi Hut](https://thepihut.com/products/raspberry-pi-5), [Pimoroni](https://shop.pimoroni.com/products/raspberry-pi-5) |
| 2 | **Pi Camera Module 3 Wide** | 12MP Sony IMX708, 120° FoV, autofocus | £32 | [The Pi Hut](https://thepihut.com/products/raspberry-pi-camera-module-3-wide), [Pimoroni](https://shop.pimoroni.com/products/raspberry-pi-camera-module-3) |
| 3 | **Camera ribbon cable (300mm)** | Longer cable for routing on hard hat | £3 | The Pi Hut, Amazon |
| 4 | **INMP441 I2S MEMS Microphone** | Digital I2S output, high SNR, small breakout | £3 | Amazon, AliExpress, eBay |
| 5 | **Bone conduction Bluetooth earpiece** | e.g. Shokz OpenRun Mini or any BT bone conduction | £30-80 | Amazon |
| 6 | **NEO-6M GPS Module** | UART output, built-in antenna, 2.5m accuracy | £8 | Amazon, The Pi Hut |
| 7 | **USB-C PD Power Bank (20,000mAh)** | Must support USB-C PD (5V/3A minimum for Pi 5) | £20-30 | Amazon |
| 8 | **MicroSD card (32GB+)** | For Raspberry Pi OS + data storage | £8 | Amazon |

## Wiring Accessories

| # | Item | Notes | Price |
|---|------|-------|-------|
| 9 | **Breadboard (half-size)** | For prototyping connections | £3 |
| 10 | **Jumper wires (F-F, M-F)** | Pack of 40, various lengths | £3 |
| 11 | **GPIO header pins** | If your Pi 5 doesn't have them pre-soldered | £1 |

## Mounting (Optional for v1)

| # | Item | Notes | Price |
|---|------|-------|-------|
| 12 | **Hard hat** | Standard site hard hat | £8-15 |
| 13 | **Velcro strips + zip ties** | For mounting Pi + battery to hard hat | £3 |
| 14 | **Small project case** | Protect the Pi from weather (or 3D print) | £5 |

## Total Estimate

| Category | Cost |
|----------|------|
| Electronics | ~£140 |
| Accessories | ~£10 |
| Mounting | ~£20 |
| **Total** | **~£170** |

## Notes

- The **bone conduction earpiece** is the most variable cost item. Cheap ones (~£15 on Amazon) will work for prototyping. Shokz are the gold standard but not needed for v1.
- The **USB-C PD power bank** must support Power Delivery — the Pi 5 draws up to 5V/5A and will undervolt with a basic USB-A power bank. Look for "PD" or "PPS" on the spec sheet.
- You do NOT need a monitor/keyboard after initial setup — the Pi runs headless over SSH/WiFi.
- All I2S wiring for the mic uses standard GPIO pins — no HATs or shields needed.
