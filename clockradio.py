from machine import Pin, I2C, SPI, disable_irq, enable_irq  # SPI is a class associated with the machine library. 
import time
import utime


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

class Radio:
    
    def __init__( self, NewFrequency, NewVolume, NewMute ):

#
# set the initial values of the radio
#
        self.Volume = 2
        self.Frequency = 88
        self.Mute = False
#
# Update the values with the ones passed in the initialization code
#
        self.SetVolume( NewVolume )
        self.SetFrequency( NewFrequency )
        self.SetMute( NewMute )
        
      
# Initialize I/O pins associated with the radio's I2C interface

        self.i2c_sda = Pin(26)
        self.i2c_scl = Pin(27)

#
# I2C Device ID can be 0 or 1. It must match the wiring. 
#
# The radio is connected to device number 1 of the I2C device
#
        self.i2c_device = 1 
        self.i2c_device_address = 0x10

#
# Array used to configure the radio
#
        self.Settings = bytearray( 8 )


        self.radio_i2c = I2C( self.i2c_device, scl=self.i2c_scl, sda=self.i2c_sda, freq=200000)
        self.ProgramRadio()

    def SetVolume( self, NewVolume ):
#
# Conver t the string into a integer
#
        try:
            NewVolume = int( NewVolume )
            
        except:
            return( False )
        
#
# Validate the type and range check the volume
#
        if ( not isinstance( NewVolume, int )):
            return( False )
        
        if (( NewVolume < 0 ) or ( NewVolume >= 16 )):
            return( False )

        self.Volume = NewVolume
        return( True )



    def SetFrequency( self, NewFrequency ):
#
# Convert the string into a floating point value
#
        try:
            NewFrequency = float( NewFrequency )
            
        except:
            return( False )
#
# validate the type and range check the frequency
#
        if ( not ( isinstance( NewFrequency, float ))):
            return( False )
 
        if (( NewFrequency < 88.0 ) or ( NewFrequency > 108.0 )):
            return( False )

        self.Frequency = NewFrequency
        return( True )
        
    def SetMute( self, NewMute ):
        
        try:
            self.Mute = bool( int( NewMute ))
            
        except:
            return( False )
        
        return( True )

#
# convert the frequency to 10 bit value for the radio chip
#
    def ComputeChannelSetting( self, Frequency ):
        Frequency = int( Frequency * 10 ) - 870
        
        ByteCode = bytearray( 2 )
#
# split the 10 bits into 2 bytes
#
        ByteCode[0] = ( Frequency >> 2 ) & 0xFF
        ByteCode[1] = (( Frequency & 0x03 ) << 6 ) & 0xC0
        return( ByteCode )

#
# Configure the settings array with the mute, frequency and volume settings
#
    def UpdateSettings( self ):
        
        if ( self.Mute ):
            self.Settings[0] = 0x80
        else:
            self.Settings[0] = 0xC0
  
        self.Settings[1] = 0x09 | 0x04
        self.Settings[2:3] = self.ComputeChannelSetting( self.Frequency )
        self.Settings[3] = self.Settings[3] | 0x10
        self.Settings[4] = 0x04
        self.Settings[5] = 0x00
        self.Settings[6] = 0x84
        self.Settings[7] = 0x80 + self.Volume

#        
# Update the settings array and transmitt it to the radio
#
    def ProgramRadio( self ):

        self.UpdateSettings()
        self.radio_i2c.writeto( self.i2c_device_address, self.Settings )

#
# Extract the settings from the radio registers
#
    def GetSettings( self ):
#        
# Need to read the entire register space. This is allow access to the mute and volume settings
# After and address of 255 the 
#
        self.RadioStatus = self.radio_i2c.readfrom( self.i2c_device_address, 256 )

        if (( self.RadioStatus[0xF0] & 0x40 ) != 0x00 ):
            MuteStatus = False
        else:
            MuteStatus = True
            
        VolumeStatus = self.RadioStatus[0xF7] & 0x0F
 
 #
 # Convert the frequency 10 bit count into actual frequency in Mhz
 #
        FrequencyStatus = (( self.RadioStatus[0x00] & 0x03 ) << 8 ) | ( self.RadioStatus[0x01] & 0xFF )
        FrequencyStatus = ( FrequencyStatus * 0.1 ) + 87.0
        
        if (( self.RadioStatus[0x00] & 0x04 ) != 0x00 ):
            StereoStatus = True
        else:
            StereoStatus = False
        
        return( MuteStatus, VolumeStatus, FrequencyStatus, StereoStatus )

#
# initialize the FM radio
#
fm_radio = Radio( 100.3, 2, False )

while ( True ):

#
# display the menu
#
    
    print("")
    print( "ECE 299 FM Radio Demo Menu" );
    print("")
    print( "1 - change radio frequency" )
    print( "2 - change volume level" )
    print( "3 - mute audio" )
    print( "4 - read current settings" )
    
    select = input( "Enter menu number > " )

#
# Set radio frequency
#
    if ( select == "1" ):
        Frequency = input( "Enter frequncy in Mhz ( IE 100.3 ) > " )

        if ( fm_radio.SetFrequency( Frequency ) == True ):
            fm_radio.ProgramRadio()
        else:
            print( "Invalid frequency( Range is 88.0 to 108.0 )" )

#
# Set volume level of radio
#
    elif ( select == "2" ):
        Volume = input( "Enter volume level ( 0 to 15, 15 is loud ) > " )
        
        if ( fm_radio.SetVolume( Volume ) == True ):
            fm_radio.ProgramRadio()
        else:
            print( "Invalid volume level( Range is 0 to 15 )" )
        
#        
# Enable mute of radio       
#        
    elif( select == "3" ):
        Mute = input( "Enter mute ( 1 for Mute, 0 for audio ) > " )
        
        if ( fm_radio.SetMute( Mute ) == True ):
            fm_radio.ProgramRadio()
        else:
            print( "Invalid mute setting" )

#
# Display radio current settings
#
    elif( select == "4" ):
        Settings = fm_radio.GetSettings()

        print( Settings )
        print("")
        print("Radio Status")
        print("")

        print( "Mute: ", end="" )
        if ( Settings[0] == True ):
            print( "enabled" )
        else:
            print( "disabled" )

        print( "Volume: %d" % Settings[1] )

        print( "Frequency: %5.1f" % Settings[2] )

        print( "Mode: ", end="" )
        if ( Settings[3] == True ):
            print( "stereo" )
        else:
            print( "mono" )


    else:
        print( "Invalid menu option" )

  
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