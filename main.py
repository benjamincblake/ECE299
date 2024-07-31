from machine import Pin, I2C, SPI, disable_irq, enable_irq,Timer,PWM  # SPI is a class associated with the machine library. 
import time
import utime
from rotary_irq_rp2 import RotaryIRQ



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
ROTARY_BUTTON = machine.Pin(16, machine.Pin.IN, machine.Pin.PULL_UP)

AlarmPWM = PWM(Pin(0, mode=Pin.OUT))
AlarmPWM.freq(500)

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
isSnoozed = False
snoozeTimer = 0

tick = 0
sel_last_tick = 0
snooze_last_tick = 0

current_val = 0

volume = 0

radioMute = True
currState = 0
menuState = 0
alarmState = 0
radioState = 0
timeState = 0

hourScroll = 1
hourSelect = False
formatSelect = 0
minuteScroll = 0

alarmFreqScroll = 4
alarmDutyScroll = 1
AlarmDuty = 49152
snoozeScroll = 5
snoozeLength = 15

radioScroll = 101.9
currentStation = 101.9

volumeScroll = 1
currentVolume = 2



def tick_counter(timer):
    global tick
    tick += 1

test_timer = Timer(mode=Timer.PERIODIC, period=1, callback=tick_counter)


#inturrept handler function for the button, sleeps for 50ms for button debounce then increments count and re-enables interupt 
def DOWNhandler(x):
    state = disable_irq()
    #down button handle
    enable_irq(state)

def SELECThandler(x):
    global tick
    global sel_last_tick
    global AlarmIsTriggered
    global AlarmToggle
    global AlarmMinutes
    global AlarmHours
    global currState
    global menuState
    global timeState
    global time_format
    global hourSelect
    global formatSelect
    global hourScroll
    global minuteScroll
    global alarmState
    global alarmFreqScroll
    global alarmDutyScroll
    global AlarmPWM
    global AlarmDuty
    global snoozeScroll
    global snoozeLength
    global fm_radio
    global radioMute
    global radioState
    global radioScroll
    global currentStation
    global volumeScroll
    global currentVolume
    
    state = disable_irq()
    if((tick - sel_last_tick) > 250):
        print("select")
        if(AlarmIsTriggered):
            AlarmIsTriggered = False
            AlarmPWM.duty_u16(0)
            fm_radio = Radio(currentStation, currentVolume, radioMute)
            
        
        elif currState == 0:
            menuState = 0
            currState = 1
            rotary.set(0, 0, 1, 3, None, None)
            
        elif currState == 1:
            if menuState == 0:
                timeState = 0
                currState = 2
                rotary.set(0, 0, 1, 2, None, None)
                
            elif menuState == 1:
                alarmState = 0
                currState = 3
                rotary.set(0, 0, 1, 3, None, None)
                
            elif menuState == 2:
                radioState = 0
                currState = 4
                rotary.set(0, 0, 1, 3, None, None)
                
            else:
                currState = 0
        
        elif currState == 2:
            if timeState == 0:
                hourScroll = 1
                minuteScroll = 0
                hourSelect = False
                currState = 5
                if time_format == 0:
                    rotary.set(0, 0, 1, 23, None, None)
                else:
                    rotary.set(1, 1, 1, 12, None, None)
                
            elif timeState == 1:
                if time_format == 0:
                    selectTimeFormat(1)
                else:
                    selectTimeFormat(0)
            else:
                rotary.set(0, 0, 1, 3, None, None)
                menuState = 0
                currState = 1
                
        elif currState == 3:
            if alarmState == 0:
                if AlarmToggle:
                    AlarmToggle = False
                else:
                    AlarmToggle = True
                    if AlarmHours == 0 and AlarmMinutes == 0 and time_format == 1:
                        setAlarm(1,12,0,0,False)
                        
                
            elif alarmState == 1:
                hourScroll = 1
                minuteScroll = 0
                hourSelect = False
                currState = 7
                if time_format == 0:
                    rotary.set(0, 0, 1, 23, None, None)
                else:
                    rotary.set(1, 1, 1, 12, None, None)
                
            elif alarmState == 2:
                currState = 9
                alarmFreqScroll = 4
                alarmDutyScroll = 1
                rotary.set(4, 4, 1, 7, None, None)
                
            else:
                rotary.set(0, 0, 1, 3, None, None)
                menuState = 0
                currState = 1
        
        elif currState == 4:
            if radioState == 0:
                if radioMute:
                    radioMute = False
                else:
                    radioMute = True
                fm_radio = Radio(currentStation, currentVolume, radioMute)
            
            elif radioState == 1:
                radioScroll = 101.9
                currState = 12
                rotary.set(101.9, 88.0, 0.1, 108.0, None, None)
                
                
            elif radioState == 2:
                volumeScroll = 1
                currState = 13
                rotary.set(1, 1, 1, 10, None, None)
            
            else:
                rotary.set(0, 0, 1, 3, None, None)
                menuState = 0
                currState = 1
                    
        
        elif currState == 5:
            if time_format == 0:
                rotary.set(0, 0, 1, 59, None, None)
                currState = 6
            elif not hourSelect:
                rotary.set(0, 0, 1, 1, None, None)
                hourSelect = True
            else:
                currState = 6
                rotary.set(0, 0, 1, 59, None, None)
        
        elif currState == 6:
            if time_format == 1:
                if formatSelect == 1:
                    setTime_12(hourScroll,minuteScroll,0,True)
                else:
                    setTime_12(hourScroll,minuteScroll,0,False)
            else:
                setTime_24(hourScroll,minuteScroll,0)
        
            currState = 2
            timeState = 0
            rotary.set(0, 0, 1, 2, None, None)
        
        elif currState == 7:
            if time_format == 0:
                rotary.set(0, 0, 1, 59, None, None)
                currState = 8
            elif not hourSelect:
                rotary.set(0, 0, 1, 1, None, None)
                hourSelect = True
            else:
                currState = 8
                rotary.set(0, 0, 1, 59, None, None)
        
        elif currState == 8:
            if time_format == 1:
                if formatSelect == 1:
                    setAlarm(1,hourScroll,minuteScroll,0,True)
                else:
                    setAlarm(1,hourScroll,minuteScroll,0,False)
            else:
                setAlarm(0,hourScroll,minuteScroll,0, False)
        
            currState = 3
            AlarmState = 0
            rotary.set(0, 0, 1, 3, None, None)
        
        elif currState == 9:
            currState = 10
            rotary.set(1, 1, 1, 4, None, None)
        
        elif currState == 10:
            AlarmPWM.freq(alarmFreqScroll*100)
            if alarmDutyScroll == 4:
                AlarmDuty = 16384
            if alarmDutyScroll == 3:
                AlarmDuty = 32768
            if alarmDutyScroll == 2:
                AlarmDuty = 49152
            if alarmDutyScroll == 1:
                AlarmDuty = 65535
            
            currState = 11
            snoozeScroll = 5
            rotary.set(5, 5, 5, 600, None, None)
            
        elif currState == 11:
            
            snoozeLength = snoozeScroll
            currState = 3
            AlarmState = 0
            rotary.set(0, 0, 1, 3, None, None)
            
        elif currState == 12:
            currentStation = radioScroll
            fm_radio = Radio(currentStation, currentVolume, radioMute)
            radioState = 0
            currState = 4
            rotary.set(0, 0, 1, 3, None, None)
            
        elif currState == 13:
            currentVolume = volumeScroll
            fm_radio = Radio(currentStation, currentVolume, radioMute)
            radioState = 0
            currState = 4
            rotary.set(0, 0, 1, 3, None, None)
            
        sel_last_tick = tick
    enable_irq(state)

def UPhandler(x):
    state = disable_irq()
    #up button handle
    enable_irq(state)

def SNOOZEhandler(x):
    global AlarmIsTriggered
    global isSnoozed
    global tick
    global snooze_last_tick
    global radioMute
    global fm_radio
    global currentStation
    global currentVolume
    state = disable_irq()
    if((tick - snooze_last_tick) > 200):
        print("snooze")
        if(AlarmIsTriggered):
            isSnoozed = True
            AlarmIsTriggered = False
            AlarmPWM.duty_u16(0)
            fm_radio = Radio(currentStation, currentVolume, radioMute)
            
        snooze_last_tick = tick
    enable_irq(state)
    

rotary = RotaryIRQ(17, 18)

rotary.set(0, 0, 1, 9, None, None)


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
    global isSnoozed
    global snoozeTimer
    global snoozeLength
    global AlarmDuty
    global fm_radio
    global AlarmPWM
    global currentStation
    global currentVolume

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
            fm_radio = Radio(currentStation, currentVolume, True)
            AlarmPWM.duty_u16(AlarmDuty)
            

        if(isSnoozed):
            snoozeTimer += 1
        
        if(snoozeTimer == snoozeLength):
            snoozeTimer = 0
            AlarmIsTriggered = True
            isSnoozed = False
            fm_radio = Radio(currentStation, currentVolume, True)
            AlarmPWM.duty_u16(AlarmDuty)

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
    global isSnoozed
    global snoozeTimer
    global snoozeLength
    global AlarmDuty
    global fm_radio
    global AlarmPWM
    global currentStation
    global currentVolume

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
            fm_radio = Radio(currentStation, currentVolume, True)
            AlarmPWM.duty_u16(AlarmDuty)
        
        if(isSnoozed):
            snoozeTimer += 1
        
        if(snoozeTimer == snoozeLength):
            snoozeTimer = 0
            isSnoozed = False
            AlarmIsTriggered = True
            fm_radio = Radio(currentStation, currentVolume, True)
            AlarmPWM.duty_u16(AlarmDuty)

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

selectTimeFormat(1)


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
    
    def ToggleMute(self, state):
        self.Mute = state

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
fm_radio = Radio(currentStation, currentVolume, radioMute)

utime.sleep(1)

#utime.sleep(1)

#AlarmPWM.duty_u16(0)
#fm_radio = Radio( 101.9, 2, False )



while ( True ):
    
    new_val = rotary.value()  # What is the encoder value right now?
    
    if current_val != new_val:  # The encoder value has changed!
        
        if currState == 1:
            menuState = new_val
            if menuState > 3:
                menuState = 3
                rotary.set(3, 0, 1, 3, None, None)
                
            if menuState < 0:
                menuState = 0
                rotary.set(0, 0, 1, 3, None, None)
        
        if currState == 2:
            timeState = new_val
            if timeState > 2:
                menuState = 2
                rotary.set(2, 0, 1, 2, None, None)
                
            if timeState < 0:
                menuState = 0
                rotary.set(0, 0, 1, 2, None, None)
                
        if currState == 3:
            alarmState = new_val
            if alarmState > 3:
                alarmState = 3
                rotary.set(3, 0, 1, 3, None, None)
                
            if alarmState < 0:
                alarmState = 0
                rotary.set(0, 0, 1, 3, None, None)
        
        if currState == 4:
            radioState = new_val
            if radioState > 3:
                radioState = 3
                rotary.set(3, 0, 1, 3, None, None)
                
            if radioState < 0:
                radioState = 0
                rotary.set(0, 0, 1, 3, None, None)
                
                
        if currState == 5 or currState == 7:
            if hourSelect:
                formatSelect = new_val
                if formatSelect > 1:
                    formatSelect = 1
                    rotary.set(1, 0, 1, 1, None, None)
                
                if formatSelect < 0:
                    formatSelect = 0
                    rotary.set(0, 0, 1, 1, None, None)
                
            elif time_format == 1:
                hourScroll = new_val
                if hourScroll > 12:
                    hourScroll = 12
                    rotary.set(12, 1, 1, 12, None, None)
                
                if hourScroll < 1:
                    hourScroll = 1
                    rotary.set(1, 1, 1, 12, None, None)
            else:
                hourScroll = new_val
                if hourScroll > 23:
                    hourScroll = 23
                    rotary.set(23, 0, 1, 23, None, None)
                
                if hourScroll < 0:
                    hourScroll = 0
                    rotary.set(0, 0, 1, 23, None, None)
        
        if currState == 6 or currState == 8:
            minuteScroll = new_val
            if minuteScroll > 59:
                minuteScroll = 59
                rotary.set(59, 0, 1, 59, None, None)
                
            if minuteScroll < 0:
                minuteScroll = 0
                rotary.set(0, 0, 1, 59, None, None)
        
        if currState == 9:
            alarmFreqScroll = new_val
            if alarmFreqScroll > 7:
                alarmFreqScroll = 7
                rotary.set(7, 4, 1, 7, None, None)
                
            if alarmFreqScroll < 4:
                alarmFreqScroll = 4
                rotary.set(4, 4, 1, 7, None, None)
        
        if currState == 10:
            alarmDutyScroll = new_val
            if alarmDutyScroll > 4:
                alarmDutyScroll = 4
                rotary.set(4, 1, 1, 4, None, None)
                
            if alarmDutyScroll < 1:
                alarmDutyScroll = 1
                rotary.set(1, 1, 1, 4, None, None)
        
        if currState == 11:
            snoozeScroll = new_val
            if snoozeScroll > 600:
                snoozeScroll = 600
                rotary.set(600, 5, 5, 600, None, None)
            
            if snoozeScroll < 5:
                snoozeScroll = 5
                rotary.set(5, 5, 5, 600, None, None)
        
        if currState == 12:
            radioScroll = new_val
            
            if radioScroll > 108.0:
                radioScroll = 108.0
                rotary.set(108.0, 88.0, 0.1, 108.0, None, None)
            
            if radioScroll < 88.0:
                radioScroll = 88.0
                rotary.set(88.0, 88.0, 0.1, 108.0, None, None)
                
        if currState == 13:
            volumeScroll = new_val
            
            if volumeScroll > 10:
                volumeScroll = 10
                rotary.set(1, 1, 1, 10, None, None)
            
            if volumeScroll < 1:
                volumeScroll = 1
                rotary.set(1, 1, 1, 10, None, None)
        
        print(fm_radio.GetSettings())
        current_val = new_val


    if AlarmIsTriggered:
        while AlarmIsTriggered:
            buffer1 = bytearray(b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x90\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x13\xb0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc7\xeb\xe0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x1f\xdf\xc0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\xfb\xfb\xb0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\t/\xb7\xb0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xbf\xfc\x00\x00\x00@\x00\x00\x00\x00\x00\x00\x00\x00?\xbd\xef\xfc\x00\x00\x00\x11\x00\x00\x00\x00\x00\x00\x00\x00\x03\xfe\xfb\xfb\x00\x00\x00e\x00\x00\x00\x00\x00\x00\x00\x00}\xb7\x7f\xff\xc0\x00\x00\n\xc0\x00\x00\x00\x00\x00\x00\x00-\x7f\xeb\x7f\xe0\x00\x00C)\x00\x00\x00\x00\x00\x00\x00?\xde\xff\xb7\xd0\x00\x00\x12\xc1\x00\x00\x00?\xfc\x00\x07\xba\xff\xfc\xfe\xf8\x00\x00\x05w\x00\x00\x01\xbf\xfd\x00\x07\xfe\xfb\xf8\x00\xe0\x00\x00\x01\xef\xd0\x00\x03\xbe\xdfx?\xdf\xff\xfa\x00\x00\x00\x00\x01\xff\xf0\x00\x1f\xff\xbb\xff\xdf\xbf\xdf\xf0\x00\x00\x00\x00\x03\xafx\x01\xfe\xd7\xaf\xd4\xb7\xbf\xdf`\x00\x00\x00\x00\x02g\xfb\x0f_\xdd\xfa\xfd\xff\xfe\xfd@\x00\x00\x00\x00\x01}\x9f\xf3\xf6\xff\xdf\xff\xdfn\xbf\x80\x00\x00\x00\x00\x00\xef\xff\xde?\xff\xfb\xdf\xdf\xfb\xff\x80\x00\x00\x00\x00\x00}}t=\xaf\xfe\xdf\xff\x7f_\x00\x00\x00\x00\x00\x00_\xf7\xf0;\xbd\xffuo\xba\xff\x00\x00\x00\x00\x00\x00\x1f\xfd\xc0?\xeb\xdb\xd7\xff_~\x80\x00\x00\x00\x00\x00\x07\xff\x00\x1e\xfe\xdb\xdf\xff\xed\xff\x00\x00\x00\x00\x00\x00\x01t\x00\x1f\xfb\x7f\xff\xf7\xfd\xd9\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0f\x7f\xfb\xbf\xfd\xff\xf9\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\xff\xf7\xe6\xffw\x7f\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\xf6\xdf}\xff\xfd_\x80\x00\x00\x00\x00\x00\x00\x00\x00\x01\xef\xf8\xff\xde\xbf\xef\xc0\x00\x00\x00\x00\x00\x00\x00\x00\x01\xef\xf0?\xff\xef\xfb\xf0\x00\x00\x00\x00\x00\x00\x00\x00\x00\xfbp\x07\xff\xe1\xda\xbe\x00\x00\x00\x00\x00\x00\x00\x00\x00\xfb\xa0\x00\x00\x00\x1d\xef\x00\x00\x00\x00\x00\x00\x00\x00\x01\xbb\xe0\x00\x00\x00\x0f\xd7\x00\x00\x00\x00\x00\x00\x00\x00\x03r\xe0\x00\x00\x00\x03\xe7\x00\x00\x00\x00\x00\x00\x00\x00\x03\xe3`\x00\x00\x00\x01\xff\x00\x00\x00\x00\x00\x00\x00\x00\x02\x83\xd0\x00\x00\x00\x00\xde\x00\x00\x00\x00\x00\x00\x00\x00\x03\xc0\xf0\x00\x00\x00\x00|\x00\x00\x00\x00\x00\x00\x00\x00\x01\xc0p\x00\x00\x00\x00x\x00\x00\x00\x00\x00\x00\x00\x00\x01\xe0<\x00\x00\x00\x00x\x00\x00\x00\x00\x00\x00\x00\x00\x00\xe0\x1e\x00\x00\x00\x03|\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf0N\x00\x00\x00\x0f\xec\x00\x00\x00\x00\x00\x00\x00\x00\x00\xe0\x05\x00\x00\x00\x0f\x8c\x00\x00\x00\x00\x00\x00\x00\x00\x00p\x02\x80\x00\x00\x08\x07\x00\x00\x00\x00\x00\x00\x00\x00\x00x\x01@\x00\x00\x00\x07\x80\x00\x00\x00\x00\x00\x00\x00\x008\x00`\x00\x00\x00\x03\x80\x00\x00\x00\x00\x00\x00\x00\x00\x1e\x00p\x00\x00\x00\x01\xe0\x00\x00\x00\x00\x00\x00\x00\x00\x0e\x00(\x00\x00\x00\x00\xb0\x00\x00\x00\x00\x00\x00\x00\x00\r\x00\x08\x00\x00\x00\x00\xf0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff\xff\xff\xff\xc0\x00\x00\x07\xff\xc0\x1f\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xf0\x7f\xff\xff")
            fb1 = framebuf.FrameBuffer(buffer1, 128, 64, framebuf.MONO_HLSB)

            oled.fill(0)
            oled.blit(fb1, 1, 3)
            oled.show()
            utime.sleep_ms(100)  # Adjust the delay as needed

                # Second image buffer
            buffer2 = bytearray(b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc0\r\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00&\x1b\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xbd\xf7\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00z\xe3{\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc6\xff\xe7\xc0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xfb\xbf\xfd\xe0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1f\xdf\xfe\xff\xf0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\xbf\xff}\xf8\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00?\xfa\xff\xff\xfc\x00\x00\x00\x00\x00\x00\x00\x01\xfc\x00\x00=\xba\xff\xf7\xbf\x00\x00\x00\x00\x00\x00\x00\x07\x9f\x80\x00?\xff\xff\xdf\x7f\x00\x00\x00\x00\x00\x00\x00\x1f~\xff\x87\xfd\xff\xf7\xfd\xff\x80\x00\x00\x00\x00\x01\xf0?\xb7\xf7\xfd^\xdf\xffw\xb7\xe0\x00\x00\x00\x00\x0f\xff\xbf\xfe\xff\xfd\xdb\xdf\x9f\x9f\x7f\xe0\x00\x00\x00\x00z\xf7\xfd\xf7\xfd\x7f\xef\xbf\xef\x8f\xf3\xe0\x00\x00\x00\x01\xb5\x7f\xef\xbe\xf7\xf6\xde\xd5\xde\x00\x0e\xe0\x00\x00\x00\x03w\xb9\xef\xfe\xd7\xbf\xff\xf7\xd8\x00\x01\xc0\x00\x00\x00\x06\xfe\xc1\xf7\xdf\xff\xdf\xfd\xef\xf0\x00\x00\x00\x00\x00\x00\x17\xfb\x83\xff\xf6\xf7_\xbf\xe9\xe0\x00\x00\x00\x00\x00\x00}\xd7\x03}{\x7f\xfd}\xf7\x80\x00\x00\x00\x00\x00\x00:\xde\x03\xfd\xfbw\xbd\xbf\xd6\x80\x00\x00\x00\x00\x00\x0f\xfd\xec\x03\xd2\xff\xef\x7f\xf7\xb5\xc0\x00\x00\x00\x00\x01_\xfd\xa8\x03\xf6\xef\xf9\x7f\xff\xbf\xc0\x00\x00\x00\x00\x00\x83\xff\xe0\x07\xff\xff\xff\xbb\xff_\xc0\x00\x00\x00\x00\x07\xbe\xfeP\x0f\xbc\xff\xfb\xff\xff\xf7\x80\x00\x00\x00\x00\x00~\xff\x80\x0f\xf5\xdf\xbf\xff\xff\xff\x80\x00\x00\x00\x00\x03\x9b\xe5\xc0\x0f\xff\xf7\xff\xff\xf7s\x00\x00\x00\x00\x00\x00\x1bl\x00\x7f\xfd\xbb\xf3\xf7\xd6}\xc0\x00\x00\x00\x00\x00\x000\x00}\xfb\xd6\x1e\xff\xff\xfe\xb0\x00\x00\x00\x00\x00\x00\x00\x0b\xdf\x7f\xf8\x01\xf7\xf7\xba\xb0\x00\x00\x00\x00\x00\x00\x00\x03\xae\xb5\xf0\x00\x7f\xeb\xff\xd8\x00\x00\x00\x00\x00\x00\x00\r\xfc\xff@\x00\x00\r\xef\x9e\x00\x00\x00\x00\x00\x00\x00\x0f\xe3\xff\xc0\x00\x00\x0f\xe2\xff\x00\x00\x00\x00\x00\x00\x00\x1d\xc7\xfe\x00\x00\x00\x07\xe1\xb7\x80\x00\x00\x00\x00\x00\x00?\x1f\xf8\x00\x00\x00\x03\xe0\x0f\xc0\x00\x00\x00\x00\x00\x00<\x1e\xf0\x00\x00\x00\x03\xe0\x07\xe0\x00\x00\x00\x00\x00\x00\xe8\x17\xc0\x00\x00\x00\x01\xe0\x00\xf0\x00\x00\x00\x00\x00\x00\xf0\x19\x00\x00\x00\x00\x00\xe0\x008\x00\x00\x00\x00\x00\x03@>\x00\x00\x00\x00\x00\xf0\x00\x1c\x00\x00\x00\x00\x00\x06@|\x00\x00\x00\x00\x00\xf0\x00\x0f\x00\x00\x00\x00\x00\x0e\x80X\x00\x00\x00\x00\x00p\x00\x07\x80\x00\x00\x00\x00\x0f\x00p\x00\x00\x00\x00\x00X\x00\x03x\x00\x00\x00\x00\x0f\x00\xe0\x00\x00\x00\x00\x00x\x00\x00\xf6\x00\x00\x00\x00\xfe\x00\xe0\x00\x00\x00\x00\x00\x18\x00\x00\x14\x00\x00\x00\x00\xf8\x01\xe0\x00\x00\x00\x00\x00\x18\x00\x008\x00\x00\x00\x00\xf0\x03\xc0\x00\x00\x00\x00\x00\x1c\x00\x00\x00\x00\x00\x00\x00\xf0\x06\x80\x00\x00\x00\x00\x00\x1c\x00\x00\x00\x00\x00\x00\x00\xc0\x07\x80\x00\x00\x00\x00\x00\x0c\x00\x00\x00\x00\x00\x00\x00\x00\x0b\x00\x00\x00\x00\x00\x00\x06\x00\x00\x00\x00\x00\x00\x00\x00\x0f\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x0b\x00\x00\x00\x00\x00\x00\x0f\x00\x00\x00\x00\x00\x00\x00\x00|\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\xb8\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\xf0\x00\x00\x00\x00\x00\x00\x03\xc0\x00\x00\x00\x00\x00\x00\x00\xe0\x00\x00\x00\x00\x00\x00\x03\xc0\x00\x00\x00\x00\x00\x00\x00\xe0\x00\x00\x00\x00\x00\x00\x03\xe0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")
            fb2 = framebuf.FrameBuffer(buffer2, 128, 64, framebuf.MONO_HLSB)

            oled.fill(0)
            oled.blit(fb2, 1, 1)
            oled.show()
            utime.sleep_ms(100)  # Adjust the delay as needed

                # Third image buffer
            buffer3 = bytearray(b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0c\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x0e\xc0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0f\x7f\xe0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x07\x81\xff\xe0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00?\xde\xf0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\xff7\xd7\xbc\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x14\xfe\xbb\xf7\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1c\x1f\xbdv\xef\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00}\xbd\xdf\xeb\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xfe\xde\xaf\xb7\xc0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\x1f\xed\xd7_\xe0\x00\x00\x00\x00\x00\x00 \x00\x00\x00\x00\xff\xff_\xdf\xf8\x00\x00\x00\x00\x00\x02\xff\xf0\x00\x00O\xff\xfe\xbf\xff\xfc\x00\x00\x00\x7f\x80\x1e\xef\xde\x00\x00\xff{\xff\xff\xfe\xff\x00\x00\x00\x7f\xf8?\xdb\xbb\xe0\x0f\xee\xff\xbf\xb6\xdf\xef\x00\x00\x07\xf7\xef\xff}\xff\xff\xff\xfd\xff\xdf\xdc\xfb\xf7\x00\x00'\xbf\xff\xff\xd7\xff\xff\xff\xff\xd5\xff\xd8\x00<\x00\x00\x1f\xfd\x81\xf7\xbf\xff\xff\xff\xfe\xbf~\xb8\x00\x1c\x00\x00\xf7\xde\x01\xff\xde\x7f\xdf\xbe\xf5\xf6\xff`\x00\x00\x00\x00\x7f\xfc\x01\xbf\xf7}\xff\xff\xbd\xdf\x7f\xc0\x00\x00\x009\xdf\xf8\x03\xf7\xdf\xbf\xff_\xff\xff\xff\x80\x00\x00\x00\x03\xfe\xf0\x03\xfd\xef\xfb\xea\xbf\xfb\xbd\xfb\x80\x00\x00\x00{\xf7@\x03\xff\xfb[\xfb\xff\xff\xfd\xee\x00\x00\x00:\xff\xf7\x00\x02\xfa\xff\x7f\xff\xed\xf4\xff\xf4\x00\x00\x00\x00?\xc5\x00\x03}\xff\xff\xf7\xff\xdb\xf6\xf8\x00\x00\x00\x00\x7f\x18\x00\x01\xbf\xff\xfd\xbf\xed\xff\x7f\xf0\x00\x00\x00<^`\x00\x01\x7f\x7f\xfe\xff\xfe\xb5\xff\xf0\x00\x00\x00\x00\x00\x00\x00\x00\xbfz\xff\xff\xff\xff\xee\xb0\x00\x00\x00\x00\x00\x00\x00\x00_\xbf\xdf\xff\xdf\xff\xff\xf0\x00\x00\x00\x00\x00\x00\x00\x00/\xff\xfd\xd7w\xddo\xe0\x00\x00\x00\x00\x00\x00\x00\x00\x15\xfb\xfd\xd7\xee\xfd\xff\xa0\x00\x00\x00\x00\x00\x00\x00\x00\x1b\xdf\xff\xee\xff\xeb\x9f@\x00\x00\x00\x00\x00\x00\x00\x00\x1f\xfd\xdf\x7f\xff\xf7\xfb\x80\x00\x00\x00\x00\x00\x00\x00\x00\r\xb7\xe1\xfe\xdf\xaf\xfe\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1f\xff\xc0\xff\xdf\xf7\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x17\xef@\x7f\xef\x7f\xfe\x00\x00\x00\x00\x00\x00\x00\x00\x00w\xff\x80\x03\xfd\xef\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xf7\x00\x008\x8f\x7f\x00\x00\x00\x00\x00\x00\x00\x00\x00\xffj\x00\x00\x00\x07\xfb\x00\x00\x00\x00\x00\x00\x00\x00\x00\xfez\x00\x00\x00\x0f_\x00\x00\x00\x00\x00\x00\x00\x00\x00|_\x000\x00\x0f\x7f\x00\x00\x00\x00\x00\x00\x00\x00\x007;\x808\x00\x0f\xf7\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1b\x1f\xe0\xfd\x80\x0f\xdf\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0f\x87\xf0\xff\xe0\x1d\x9f\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\xc0\xdc\x03\xff\xbd\x1f\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\xf0>\x01\xfb\xfe\x1f\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xd0\x1f\x00O\xee\x1d\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00t\x07\xc0\x00\xfc~\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00>\x01@\x00\t\xbe\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1f\x00\xc0\x00\x07\xbc\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x07\x80\xb0\x00?\xc0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\x80\xb8\x00\xfe\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\x80\xd8?\xf8\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x07\x80\x00;\xe0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x07\x80\x00.\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")
            fb3 = framebuf.FrameBuffer(buffer3, 128, 64, framebuf.MONO_HLSB)

            oled.fill(0)
            oled.blit(fb3, 1, 1)
            oled.show()
            utime.sleep_ms(100)  # Adjust the delay as needed


            oled.show()
        
        



# Clear the buffer
#
    oled.fill(0)

        
#
# Update the text on the screen
#
    if currState == 0:
        
        #Speaker Icon
        buffer1 = bytearray(b"\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\xc2\x01\x01\xc1\x01\x03\xc5\x00\x07\xc5\x80\x7f\xd6\x80o\xda\x80\x7f\xca\x80]\xca\x80\x7f\xda\x00\x7f\xd2\x80\x06\xd6\x80\x03\xc5\x80\x01\xc5\x00\x00\xc3\x01\x00@\x00\x00\x00\x00\x00\x00\x00")
        fb1 = framebuf.FrameBuffer(buffer1, 20, 20, framebuf.MONO_HLSB)

        #Radio Icon
        buffer2 = bytearray(b"\x00\x00\x00\x0c\x03\x00\x1c\x03\x00\x1b\r\x806\x0e\x806\xe6\xc04\xf2\xc0$\xf2\xc04\xf2\xc04\xf6\xc06f\xc0\x13m\x80\x18a\x80\x0cc\x00\x00`\x00\x00`\x00\x00`\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")
        fb2 = framebuf.FrameBuffer(buffer2, 20, 20, framebuf.MONO_HLSB)
                             #\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc2\x00\x01\xc1\x00\x03\xc5\x00\x07\xc5\x80\x7f\xd6\x80o\xda\x80\x7f\xca\x80]\xca\x80\x7f\xda\x00\x7f\xd2\x80\x06\xd6\x80\x03\xc5\x80\x01\xc5\x00\x00\xc3\x00\x00@\x00\x00\x00\x00\x00\x00\x00

        #Alarm
        buffer3 = bytearray(b"\x00\x00\x00\x1c\x03\x80x\x01\xe0`\x00`\xce\x070\xcc\x030\xd8a\xb0\x18\xf1\x80\x01\xf8\x00\x03\xfc\x00\x03\xfc\x00\x03\xfc\x00\x03\xfc\x00\x07\xfe\x00\x0f\xff\x00\x0f\xff\x00\x00\x00\x00\x00`\x00\x00`\x00\x00\x00\x00")
        fb3 = framebuf.FrameBuffer(buffer3, 20, 20, framebuf.MONO_HLSB)
        
        if time_format == 0:
            oled.text("{:02d}:{:02d}".format(hours, minutes), 0, 0 )
        else:
            if Pm:
                twelveHrFormat = afternoon
            else:
                twelveHrFormat = morning
            oled.text("{:02d}:{:02d}{:02s}".format(hours, minutes, twelveHrFormat), 0, 0 )
        if AlarmToggle:
            oled.text("Alarm:",0, 10)
            
            if time_format == 0:
                oled.text("{:02d}:{:02d}".format(AlarmHours, AlarmMinutes), 47, 10 )
            else:
                if Pm:
                    twelveHrFormat = afternoon
                else:
                    twelveHrFormat = morning
                    oled.text("{:02d}:{:02d}{:02s}".format(AlarmHours, AlarmMinutes,twelveHrFormat), 47, 10 )
            oled.blit(fb3, 46, 45)
        else:
            oled.text("No Alarm Set", 0, 10)
        
        
        if not radioMute:
            oled.blit(fb2, 24, 45)
        
        oled.text("Station:", 0, 20)
        oled.text(str(fm_radio.GetSettings()[2]), 65, 20)
        oled.text("FM", 105,20)
        
        oled.text("Vol:{:02d}, Stereo".format(currentVolume), 0, 30)
        
        

        # oled.blit(fb0, 1, 1)
        oled.blit(fb1, 1, 44)
    
    if currState == 1:
        trueybuf = bytearray(b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\x08\x00\x1c\x0e\x00|\x0f\x80|\x0f\x00\x0c\x0c\x00\x0e\x0c\x00\x0e\x1c\x00\x0f<\x00\x07\xfc\x00\x07\xf8\x00\x01\xe0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")
        truey = framebuf.FrameBuffer(trueybuf, 18,18, framebuf.MONO_HLSB)
        
        
        
        oled.text("Time", 30, 5)
        oled.text("Alarm", 30, 20)
        oled.text("Radio", 30, 35)
        oled.text("Back", 30, 50)
        
        if menuState == 0:
            oled.blit(truey, 0, 0)
            
        if menuState == 1:
            oled.blit(truey, 0, 15)
            
        if menuState == 2:
            oled.blit(truey, 0, 30)
            
        if menuState == 3:
            oled.blit(truey, 0, 45)
    
    if currState == 2:
        trueybuf = bytearray(b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\x08\x00\x1c\x0e\x00|\x0f\x80|\x0f\x00\x0c\x0c\x00\x0e\x0c\x00\x0e\x1c\x00\x0f<\x00\x07\xfc\x00\x07\xf8\x00\x01\xe0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")
        truey = framebuf.FrameBuffer(trueybuf, 18,18, framebuf.MONO_HLSB)
        
        
        oled.text("Set Time", 30, 5)
        oled.text("Format:", 30, 20)
        if time_format == 0:
            oled.text("24H", 90, 20)
        else:
            oled.text("12H", 90, 20)
        oled.text("Back", 30, 35)
        
        if timeState == 0:
            oled.blit(truey, 0, 0)
            
        if timeState == 1:
            oled.blit(truey, 0, 15)
            
        if timeState == 2:
            oled.blit(truey, 0, 30)
    
    if currState == 3:
        trueybuf = bytearray(b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\x08\x00\x1c\x0e\x00|\x0f\x80|\x0f\x00\x0c\x0c\x00\x0e\x0c\x00\x0e\x1c\x00\x0f<\x00\x07\xfc\x00\x07\xf8\x00\x01\xe0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")
        truey = framebuf.FrameBuffer(trueybuf, 18,18, framebuf.MONO_HLSB)
        
        oled.text("Toggle:", 30, 5)
        if AlarmToggle:
            oled.text("ON", 90, 5)
        else:
            oled.text("OFF", 90, 5)
        oled.text("Set Time", 30, 20)
        oled.text("Customize", 30, 35)
        oled.text("Back", 30, 50)
        
        if alarmState == 0:
            oled.blit(truey, 0, 0)
            
        if alarmState == 1:
            oled.blit(truey, 0, 15)
            
        if alarmState == 2:
            oled.blit(truey, 0, 30)
            
        if alarmState == 3:
            oled.blit(truey, 0, 45)
        
    if currState == 4:
        trueybuf = bytearray(b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\x08\x00\x1c\x0e\x00|\x0f\x80|\x0f\x00\x0c\x0c\x00\x0e\x0c\x00\x0e\x1c\x00\x0f<\x00\x07\xfc\x00\x07\xf8\x00\x01\xe0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")
        truey = framebuf.FrameBuffer(trueybuf, 18,18, framebuf.MONO_HLSB)
        
        oled.text("Mute:", 30, 5)
        if radioMute:
            oled.text("ON", 75, 5)
        else:
            oled.text("OFF", 75, 5)
        oled.text("Set Freq", 30, 20)
        oled.text("Volume", 30, 35)
        oled.text("Back", 30, 50)
        
        if radioState == 0:
            oled.blit(truey, 0, 0)
            
        if radioState == 1:
            oled.blit(truey, 0, 15)
            
        if radioState == 2:
            oled.blit(truey, 0, 30)
            
        if radioState == 3:
            oled.blit(truey, 0, 45) 
    
    if currState == 5 or currState == 7:
        oled.text("Select Hour:", 0 ,0)
        if time_format == 0:
            oled.text("{:02d}".format(hourScroll), 0, 20 )
        else:
            oled.text("{:02d}".format(hourScroll), 0, 20 )
            if formatSelect == 0:
                oled.text("AM", 15, 20)
            else:
                oled.text("PM", 15, 20)
    
    if currState == 6 or currState == 8:
        oled.text("Select Minute:", 0 ,0)
        oled.text("{:02d}".format(minuteScroll), 0, 20 )
    
    if currState == 9:
        oled.text("Select Frequency:", 0, 0)
        oled.text("{:01d}".format(alarmFreqScroll), 0, 20 )
        oled.text("00HZ",8,20)
        
    if currState == 10:
        oled.text("Select Volume:", 0, 0)
        oled.text("{:01d}".format(alarmDutyScroll), 0, 20 )
        
    if currState == 11:
        oled.text("Select Snooze (s):", 0, 0)
        oled.text("{:03d}".format(snoozeScroll), 0, 20 )
    
    if currState == 12:
        oled.text("Select Frequency:", 0, 0)
        oled.text("{:.1f}MHz".format(radioScroll), 0, 20 )
        
    if currState == 13:
        oled.text("Select Volume:",0, 0)
        oled.text("{:02d}".format(volumeScroll), 0, 20 )
        
#
# Draw box below the text
#
            

#
# Transfer the buffer to the screen
#
    oled.show()




