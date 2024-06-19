#!/usr/bin/env python
"""
    This script was designed to control two peristaltic pumps via 
      a RPi4 and MCC152 HAT. The pumps are set up to run a sequence
      based on timing parameter input from the user. One pump, called 
      'media pump' is ran in reverse to pump out fluid for a given amount
      of time at a given speed and then reverse its flow for the same amount
      of time and at the same speed. Then, the 'profusion' pump will run 
      for a set time and speed. The cycle then repeats for an input number
      of times.
"""
from __future__ import print_function
from sys import version_info
from daqhats import mcc152, OptionFlags, HatIDs, HatError, DIOConfigItem
from daqhats_utils import select_hat_device
import time
import sys
# Get the min and max voltage values for the analog outputs to validate
# the user input.
MIN_V = mcc152.info().AO_MIN_RANGE
MAX_V = mcc152.info().AO_MAX_RANGE
NUM_CHANNELS = mcc152.info().NUM_AO_CHANNELS
MIN_T = 0
MAX_T = 100
Pump_0_off = 0b00000001
Pump_0_fwd = 0b00000010
Pump_1_off = 0b00000100
Pump_1_fwd = 0b00001000

pump_in_media = 0b00000110
pump_out_media = 0b00000100
pump_profusion = 0b00001001

def get_channel_speed_value(channel):
    """
    Get the voltage from the user and validate it.
    """

    if channel not in range(NUM_CHANNELS):
        raise ValueError(
            "Channel must be in range 0 - {}.".format(NUM_CHANNELS - 1))

    while True:
        speed = "   Speed for Channel {}: ".format(channel)

        if version_info.major > 2:
            str_v = input(speed)
        else:
            str_v = raw_input(speed)

        try:
            speed_value = float(str_v)
        except ValueError:
            raise
        else:
            if (speed_value < MIN_V) or (speed_value > MAX_V):
                # Out of range, ask again.
                print("Value out of range.")
            else:

                # Valid value.
                return speed_value

def get_channel_duration_value(channel):
    """
    Get the voltage from the user and validate it.
    """

    if channel not in range(NUM_CHANNELS):
        raise ValueError(
            "Channel must be in range 0 - {}.".format(NUM_CHANNELS - 1))

    while True:
        duration = "   Duration for Channel {}: ".format(channel)

        if version_info.major > 2:
            str_v = input(duration)
        else:
            str_v = raw_input(duration)

        try:
            duration_value = float(str_v)
        except ValueError:
            raise
        else:
            if (duration_value < MIN_T) or (duration_value > MAX_T):
                # Out of range, ask again.
                print("Value out of range.")
            else:

                # Valid value.
                return duration_value

def get_num_cycles():
    """
    Get the number of cycles from the user and validate it.
    """
    while True:
        cycles = "   Number of Cycles to run: "

        if version_info.major > 2:
            str_v = input(cycles)
        else:
            str_v = raw_input(cycles)

        try:
            cycles_value = int(str_v)
        except CyclesError:
            raise
        else:
            if (cycles_value < 0) or (cycles_value > 1000):
                # Out of range, ask again.
                print("Value out of range.")
            else:
                # Valid value.
                print(type(cycles_value))
                return cycles_value

def get_input_values():
    """
    Get the voltages for both channels from the user.
    """

    while True:
        print("Enter speeds for pumps between {0:.1f} and {1:.1f}, non-numeric "
              "character to exit: ".format(MIN_V, MAX_V))
        try:
            speed_values = [get_channel_speed_value(channel) for channel in
                      range(NUM_CHANNELS)]
        except ValueError:
            raise

        print("Enter durations for pumps in seconds between {0:.1f} and {1:.1f}, non-numeric "
              "character to exit: ".format(MIN_T, MAX_T))
        try:
            duration_values = [get_channel_duration_value(channel) for channel in
                       range(NUM_CHANNELS)]
        except ValueError:
            raise

        print("Enter number of cycles to run ")
        try:
            cycles = int(get_num_cycles())
        except ValueError:
            raise

        else:
            # Valid values.
            return speed_values, duration_values, cycles

def main():
    """
    This function is executed automatically when the module is run directly.
    """
    options = OptionFlags.DEFAULT

    print('This script runs two pumps using a raspberry pi and MCC152 HAT.')
    print('Pump 0 is the waste pump. Pump 1 is the profusion pump.')
    print()

    # Get an instance of the selected hat device object.
    address = select_hat_device(HatIDs.MCC_152)

    #print("\nUsing address {} for the MCC152.\n".format(address))

    hat = mcc152(address)
    hat.dio_reset()

    # set all channels as outputs.
    try:
      hat.dio_config_write_port(DIOConfigItem.DIRECTION, 0x00)
    except (HatError, ValueError):
      print("Could not configure the port as outputs.")
      sys.exit()

    run_loop = True
    error = False
    while run_loop and not error:
        # Get the values from the user.
        try:
            speed_values, duration_values, cycles = get_input_values()
        except ValueError:
            run_loop = False
            print("error")
        else:
            # Write the values.
            for cycle in range(0, cycles):
              try:
                hat.dio_output_write_port(pump_out_media)
                #print("{:08b}".format(pump_out_media))
                hat.a_out_write_all(values=speed_values, options=options)
                print("Pumping media out at ",speed_values[0]," volts for ",duration_values[0]," seconds.")
                time.sleep(duration_values[0])
                hat.dio_output_write_port(pump_in_media)
                #print("{:08b}".format(pump_in_media))
                print("Pumping new media in at ",speed_values[0], " volts for", duration_values[0]," seconds.")
                time.sleep(duration_values[0])
                hat.dio_output_write_port(pump_profusion)
                print("Pumping the profusion pump at ",speed_values[1]," volts for ",duration_values[1]," seconds.")
                time.sleep(duration_values[1])
              except (HatError, ValueError):
                print("you got yourself an error bud")
                error = True
            hat.dio_output_write_port(Pump_0_off | Pump_1_off)



if __name__ == '__main__':
    # This will only be run when the module is called directly.
    main()
