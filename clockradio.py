from machine import Pin, I2C, SPI, disable_irq, enable_irq,Timer  # SPI is a class associated with the machine library. 
import time
import utime


# The below specified libraries have to be included. Also, ssd1306.py must be saved on the Pico. 
from ssd1306 import SSD1306_SPI # this is the driver library and the corresponding class
import framebuf # this is another library for the display. 


# Define columns and rows of the oled display. These numbers are the standard values. 
SCREEN_WIDTH = 128 #number of columns
SCREEN_HEIGHT = 64 #number of rows


# Initialize I/O pins associated with the oled display SPI interface

spi_sck = Pin(10) # sck stands for serial clock; always be connected to SPI SCK pin of the Pico
spi_sda = Pin(11) # sda stands for serial data;  always be connected to SPI TX pin of the Pico; this is the MOSI
spi_res = Pin(15) # res stands for reset; to be connected to a free GPIO pin
spi_dc  = Pin(14) # dc stands for data/command; to be connected to a free GPIO pin
spi_cs  = Pin(13) # chip select; to be connected to the SPI chip select of the Pico 

#
# SPI Device ID can be 0 or 1. It must match the wiring. 
#
SPI_DEVICE = 1 # Because the peripheral is connected to SPI 0 hardware lines of the Pico

#
# initialize the SPI interface for the OLED display
#
oled_spi = SPI( SPI_DEVICE, baudrate= 100000, sck= spi_sck, mosi= spi_sda )

#
# Initialize the display
#
oled = SSD1306_SPI( SCREEN_WIDTH, SCREEN_HEIGHT, oled_spi, spi_dc, spi_res, spi_cs, True )

DOWN = machine.Pin(1, machine.Pin.IN, machine.Pin.PULL_UP)
SELECT = machine.Pin(2, machine.Pin.IN, machine.Pin.PULL_UP)
UP = machine.Pin(3, machine.Pin.IN, machine.Pin.PULL_UP)
SNOOZE = machine.Pin(4, machine.Pin.IN, machine.Pin.PULL_UP)

# Assign a value to a variable

seconds = 0
minutes = 0
hours = 0
time_format = 0
Pm = False 
morning = "AM"
afternoon = "PM"
twelveHrFormat = morning

AlarmToggle = False
AlarmIsTriggered = False
AlarmSeconds = 0
AlarmMinutes = 0
AlarmHours = 0
Alarm_PM = False


#inturrept handler function for the button, sleeps for 50ms for button debounce then increments count and re-enables interupt 
def DOWNhandler(x):
        state = disable_irq()
        #down button handle
        enable_irq(state)

def SELECThandler(x):
        state = disable_irq()
        #select button handle
        enable_irq(state)

def UPhandler(x):
        state = disable_irq()
        #up button handle
        enable_irq(state)

def SNOOZEhandler(x):
        state = disable_irq()
        #snooze button handle
        enable_irq(state)

#button ISR function call
DOWN.irq(trigger= machine.Pin.IRQ_RISING, handler = DOWNhandler)
SELECT.irq(trigger= machine.Pin.IRQ_RISING, handler = SELECThandler)
UP.irq(trigger= machine.Pin.IRQ_RISING, handler = UPhandler)
SNOOZE.irq(trigger= machine.Pin.IRQ_RISING, handler = SNOOZEhandler)

def clocktimer_24(timer):
    global seconds
    global minutes
    global hours
    global Pm
    global twelveHrFormat
    global AlarmToggle
    global AlarmSeconds
    global AlarmMinutes
    global AlarmHours
    global AlarmIsTriggered

    seconds += 1
    if seconds >= 60:
        minutes += 1
        seconds = 0
    if minutes >= 60:
        hours += 1
        minutes = 0
    if hours >= 24:
        hours = 0

    if AlarmToggle:
        if hours == AlarmHours and minutes == AlarmMinutes and seconds == AlarmSeconds:
            AlarmIsTriggered = True

def clocktimer_12(timer):
    global seconds
    global minutes
    global hours
    global Pm
    global twelveHrFormat
    global AlarmToggle
    global AlarmSeconds
    global AlarmMinutes
    global AlarmHours
    global AlarmIsTriggered
    global Alarm_PM

    seconds += 1
    if seconds >= 60:
        minutes += 1
        seconds = 0
    if minutes >= 60:
        hours += 1
        minutes = 0
    if hours == 12 and minutes == 0 and seconds == 0:
        Pm = not Pm
    if hours >= 13:
        hours = 1
    
    if AlarmToggle:
        if hours == AlarmHours and minutes == AlarmMinutes and seconds == AlarmSeconds and Pm == Alarm_PM:
            AlarmIsTriggered = True
        
soft_timer = Timer(mode=Timer.PERIODIC, period=1000, callback=clocktimer_24)

def selectTimeFormat(time):
    global hours
    global time_format
    global Pm
    global soft_timer
    global AlarmToggle
    global AlarmSeconds
    global AlarmMinutes
    global AlarmHours
    global Alarm_PM

    
    if time == 0 and time_format != 0:
        time_format = 0
        if not(Pm):
            hours = 12 + hours
            Pm = False
        soft_timer.deinit()
        soft_timer = Timer(mode=Timer.PERIODIC, period=1000, callback=clocktimer_24)

        if AlarmToggle:
            if not(Alarm_PM):
                AlarmHours = 12 + AlarmHours
                Alarm_PM = False
        
    if time == 1 and time_format != 1:
        time_format = 1
        Pm = False
        if hours > 12:
            hours = hours - 12
            Pm = True
        if hours == 0:
            hours = 12
        soft_timer.deinit()
        soft_timer = Timer(mode=Timer.PERIODIC, period=1000, callback=clocktimer_12)

        if AlarmToggle:
            Alarm_PM = False
            if AlarmHours > 12:
                AlarmHours = AlarmHours - 12
                Alarm_PM = True
            if AlarmHours == 0:
                AlarmHours = 12

def setTime_12(h,m,s,IsPM):
    global seconds
    global minutes
    global hours
    global Pm
    
    if time_format == 1:
        seconds = s
        minutes = m
        hours = h
        Pm = IsPM

def setTime_24(h,m,s):
    global seconds
    global minutes
    global hours
    
    if time_format == 0:
        seconds = s
        minutes = m
        hours = h

def setAlarm(timeFormat,h,m,s,IsPM):
    global AlarmToggle
    global AlarmSeconds
    global AlarmMinutes
    global AlarmHours
    global Alarm_PM

    AlarmHours = h
    AlarmMinutes = m
    AlarmSeconds = s

    if timeFormat == 1:
        Alarm_PM = IsPM
    
    AlarmToggle = True 

class Radio:
    
    def __init__( self, NewFrequency, NewVolume, NewMute ):

#
# set the initial values of the radio
#
        self.Volume = 2
        self.Frequency = 101.9
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
fm_radio = Radio( 101.9, 2, False )

while ( True ):
    



    if AlarmIsTriggered:
        while AlarmIsTriggered:
            oled.fill(0)
            oled.text("BEEP BOOP", 0, 0)
            oled.text("BEEP BOOP", 0, 10)
            oled.text("BEEP BOOP", 0, 20)
            oled.text("BEEP BOOP", 0, 30)
            oled.text("BEEP BOOP", 0, 40)     
            oled.text("BEEP BOOP", 0, 50)
            oled.text("BEEP BOOP", 0, 60)  

            oled.show()
        
        AlarmToggle = False



# Clear the buffer
#
    oled.fill(0)

        
#
# Update the text on the screen
#
    oled.text("Welcum to ECE", 0, 0) # Print the text starting from 0th column and 0th row
    oled.text("299", 45, 10) # Print the number 299 starting at 45th column and 10th row
    if time_format == 0:
        oled.text("{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds), 0, 30 )
    else:
        if Pm:
            twelveHrFormat = afternoon
        else:
            twelveHrFormat = morning
        oled.text("{:02d}:{:02d}:{:02d} {:02s}".format(hours, minutes, seconds, twelveHrFormat), 0, 30 )

    oled.text("{:02d}:{:02d}:{:02d}".format(AlarmHours, AlarmMinutes, AlarmSeconds), 0, 40 )

#
# Draw box below the text
#
    oled.rect( 0, 60, 128, 5, 1  )        

#
# Transfer the buffer to the screen
#
    oled.show()

#
# display the menu
#
#
# display the menu
#
    
#     print("")
#     print( "ECE 299 FM Radio Demo Menu" )
#     print("")
#     print( "1 - change radio frequency" )
#     print( "2 - change volume level" )
#     print( "3 - mute audio" )
#     print( "4 - read current settings" )
    
#     select = input( "Enter menu number > " )

# #
# # Set radio frequency
# #
#     if ( select == "1" ):
#         Frequency = input( "Enter frequncy in Mhz ( IE 100.3 ) > " )

#         if ( fm_radio.SetFrequency( Frequency ) == True ):
#             fm_radio.ProgramRadio()
#         else:
#             print( "Invalid frequency( Range is 88.0 to 108.0 )" )

# #
# # Set volume level of radio
# #
#     elif ( select == "2" ):
#         Volume = input( "Enter volume level ( 0 to 15, 15 is loud ) > " )
        
#         if ( fm_radio.SetVolume( Volume ) == True ):
#             fm_radio.ProgramRadio()
#         else:
#             print( "Invalid volume level( Range is 0 to 15 )" )
        
# #        
# # Enable mute of radio       
# #        
#     elif( select == "3" ):
#         Mute = input( "Enter mute ( 1 for Mute, 0 for audio ) > " )
        
#         if ( fm_radio.SetMute( Mute ) == True ):
#             fm_radio.ProgramRadio()
#         else:
#             print( "Invalid mute setting" )

# #
# # Display radio current settings
# #
#     elif( select == "4" ):
#         Settings = fm_radio.GetSettings()

#         print( Settings )
#         print("")
#         print("Radio Status")
#         print("")

#         print( "Mute: ", end="" )
#         if ( Settings[0] == True ):
#             print( "enabled" )
#         else:
#             print( "disabled" )

#         print( "Volume: %d" % Settings[1] )

#         print( "Frequency: %5.1f" % Settings[2] )

#         print( "Mode: ", end="" )
#         if ( Settings[3] == True ):
#             print( "stereo" )
#         else:
#             print( "mono" )


#     else:
#         print( "Invalid menu option" )
