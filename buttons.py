from gpiozero import Button
from signal import pause
import time
import subprocess
from board import SCL, SDA
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
import sys

lower_case = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
upper_case = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
symbols = ['!','"','#','$','%','&','\\','\'','(',')','*','+',',','-','.','/',':',';','<','=','>','?','@','[','\\',']','^','_','`','{','|','}','~']
numbers = [0,1,2,3,4,5,6,7,8,9]
token = []

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

button_1 = Button(27) # a
button_2 = Button(17) # A
button_3 = Button(14) # !
button_4 = Button(23) # 0
button_5 = Button(24) # delete
button_6 = Button(5) # Enter

press_count = 0
token_index = -1
first_press = True
prev_type = [-1]
start_time = time.time()
prev_time = time.time()

underscore = " "
binary = 1
odd_or_even = 0

def token_char(char_type, limit):
    
    global start_time
    global end_time
    global prev_type
    global press_count
    global token_index
    global token
    global first_press
    
    start_time = time.time()
    
    if char_type[0] == prev_type[0] and (start_time-end_time < 1.25):
        first_press = False
    else:
        first_press = True
        press_count = 0
        
    end_time = time.time()
    
    if first_press == True:
        token.append(char_type[press_count])
        first_press = False
        if token_index < len(token):
            token_index += 1 
    else:
      token[token_index] = char_type[press_count]

    if press_count < limit:
        press_count += 1
    else:
        press_count = 0

    prev_type[0] = char_type[0]
    print(*token)

def del_char():
    global token
    global token_index
    global prev_type
    
    if len(token) > 0:
        token.pop(token_index)
        
        if token_index >= 0:
         token_index -= 1
    
    prev_type[0] = -1
    print(*token)
    
def enter():
    with open('/home/pi/Desktop/AC40001/telegramBot.py') as infile:
        a = infile.read()
        sys.argv = ["telegramBot.py", token]
        exec(a)

while True:
    
    button_1.when_pressed = lambda: token_char(lower_case, 25)
    button_2.when_pressed = lambda: token_char(upper_case, 25)
    button_3.when_pressed = lambda: token_char(symbols, len(symbols)-1)
    button_4.when_pressed = lambda: token_char(numbers, 9)
    button_5.when_pressed = del_char
    button_6.when_pressed = enter

    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    
    
    displayStr = " "
    # avoid token runnning off OLED edge by limiting displayed token to 20 characters
    if len(token) > 20:
        for y in range (0, 20):
            displayStr += token[y + (len(token)-20)]
    else:
        for ele in token: 
            displayStr += ele 
    
    # Write three lines of text. Maximum characters per line = 21
    draw.text((x, top + 0), "Enter your Telegram", font=font, fill=255)
    draw.text((x, top + 8), "Bot token below :", font=font, fill=255)
    draw.text((x, top + 25), displayStr, font=font, fill=255)
    

    # Display image.
    disp.image(image)
    disp.show()
    time.sleep(0.5)