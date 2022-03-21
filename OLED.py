import time
import subprocess

from board import SCL, SDA
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306


# Create the I2C interface.
i2c = busio.I2C(SCL, SDA)

# Create the SSD1306 OLED class.
# The first two parameters are the pixel width and pixel height.  Change these
# to the right size for your display!
disp = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)

# Clear display.
disp.fill(0)
disp.show()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new("1", (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=0)

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height - padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0

font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 9)

underscore = " "
binary = 1
odd_or_even = 0
token = "333333"
while True:
    
    binary += 1
    odd_or_even = binary % 2
    if odd_or_even == 0:
        underscore = "|"
    else:
        underscore = " "
    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=0)

    # Write three lines of text. Maximum characters per line = 21
    draw.text((x, top + 0), "Enter your Telegram", font=font, fill=255)
    draw.text((x, top + 8), "Bot token below :", font=font, fill=255)
    draw.text((x, top + 25), token + underscore, font=font, fill=255)
    

    # Display image.
    disp.image(image)
    disp.show()
    time.sleep(0.5)