from machine import Pin, SPI, disable_irq, enable_irq  # SPI is a class associated with the machine library. 


# The below specified libraries have to be included. Also, ssd1306.py must be saved on the Pico. 
from ssd1306 import SSD1306_SPI # this is the driver library and the corresponding class
import framebuf # this is another library for the display. 


# Define columns and rows of the oled display. These numbers are the standard values. 
SCREEN_WIDTH = 128 #number of columns
SCREEN_HEIGHT = 64 #number of rows


# Initialize I/O pins associated with the oled display SPI interface

spi_sck = Pin(18) # sck stands for serial clock; always be connected to SPI SCK pin of the Pico
spi_sda = Pin(19) # sda stands for serial data;  always be connected to SPI TX pin of the Pico; this is the MOSI
spi_res = Pin(21) # res stands for reset; to be connected to a free GPIO pin
spi_dc  = Pin(20) # dc stands for data/command; to be connected to a free GPIO pin
spi_cs  = Pin(17) # chip select; to be connected to the SPI chip select of the Pico 

#
# SPI Device ID can be 0 or 1. It must match the wiring. 
#
SPI_DEVICE = 0 # Because the peripheral is connected to SPI 0 hardware lines of the Pico

#
# initialize the SPI interface for the OLED display
#
oled_spi = SPI( SPI_DEVICE, baudrate= 100000, sck= spi_sck, mosi= spi_sda )

#
# Initialize the display
#
oled = SSD1306_SPI( SCREEN_WIDTH, SCREEN_HEIGHT, oled_spi, spi_dc, spi_res, spi_cs, True )

bttn = machine.Pin(0, machine.Pin.IN, machine.Pin.PULL_UP)

# Assign a value to a variable
Count = 0

#inturrept handler function for the button, sleeps for 50ms for button debounce then increments count and re-enables interupt 
def bttnhandler(x):
        global Count
        state = disable_irq()
        utime.sleep_ms(50)
        Count += 1
        enable_irq(state)

#button ISR function call
bttn.irq(trigger= machine.Pin.IRQ_RISING, handler = bttnhandler)

while ( True ):

  
#
# Clear the buffer
#
        oled.fill(0)
        
#
# Update the text on the screen
#
        oled.text("Welcome to ECE", 0, 0) # Print the text starting from 0th column and 0th row
        oled.text("299", 45, 10) # Print the number 299 starting at 45th column and 10th row
        oled.text("Count is: %4d" % Count, 0, 30 ) # Print the value stored in the variable Count. 
        
#
# Draw box below the text
#
        oled.rect( 0, 50, 128, 5, 1  )        

#
# Transfer the buffer to the screen
#
        oled.show()
    