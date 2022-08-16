# include python libraries
import serial
import time
import math

##
######################BASE FUNCTIONS######################
##

def wait(time_in_ms):
    output = "M" + str(time_in_ms)
    return output

#counter-clockwise rotation to the selected valve
def change_to_valve(valve_number):
    output = "O" + str(valve_number)
    return output

#clockwise rotation by valve_distance*60 degrees
def change_to_valve_relative(valve_distance):
    output = "I" + str(valve_distance)
    return output

def change_to_valve_fastest(valve_number):
    output = "B" + str(valve_number)
    return output

#position based on gear steps
def go_to_absolute_pump_position(step_position):
    global pump_position

    if(step_position>3000 or step_position<0):
        print("Volume is overshooting, you tried to go to: " + str(step_position))
        step_position=pump_position

    pump_position = step_position

    output = "A" + str(step_position)

    return output

#position based on gear steps
def pickup_position(pickup_distance):
    global pump_position

    old_position=pump_position

    pump_position = pump_position + pickup_distance

    if(pump_position>3000):
        print("Volume is overshooting, you tried to go to: " + str(pump_position))
        pickup_distance=3000-old_position
        pump_position=3000

    output = "P" + str(pickup_distance)

    return output

#position based on gear steps
def dispense_position(dispense_distance):
    global pump_position

    old_position=pump_position

    pump_position = pump_position - dispense_distance

    if(pump_position<0):
        print("Volume is overshooting, you tried to go to: " + str(pump_position))
        dispense_distance=old_position
        pump_position=0

    output = "D" + str(dispense_distance)

    return output

def peak_speed(pulse_per_sec):
    output = "V" + str(pulse_per_sec)
    return output

#repeat sequence n times
def repeat_sequence(sequence, n):
    output = "g" + sequence + "G" + str(n)
    return output

def repeat_last_command(lsp):
    lsp.write(b"/1XR\r")

def write_sequence_to_pump(lsp, sequence):
    output = "/1"+sequence+"R\r"

    lsp.write(output.encode())

#high, normal, medium, low. low by default
def set_force(lsp, force):
    forces = {
        "high" : lsp.write(b"/1Z0R\r"),
        "normal" : lsp.write(b"/1Z1R\r"),
        "medium" : lsp.write(b"/1Z2R\r"),
        "low" : lsp.write(b"/1Z3R\r")
    }

    forces.get(force, forces.get("low")) #low by default

    time.sleep(20)
    print("Force set to " + force)

def uL_volume_to_step(volume):
    a=0.000005306
    b=0.121005573

    steps=(-b+math.sqrt(b*b+4*a*volume))/(2*a)
    steps=math.floor(steps)

    return steps

def absolute_position_uL(volume):
    return go_to_absolute_pump_position(uL_volume_to_step(volume))

def pickup_uL(volume):
    return pickup_position(uL_volume_to_step(volume))

def dispense_uL(volume):
    return dispense_position(uL_volume_to_step(volume))

def clean_with_air(cleaned_valve, air_valve):
    sequence=peak_speed(300)+wait(100)+change_to_valve_fastest(air_valve)+wait(100)+go_to_absolute_pump_position(3000)+wait(10)+change_to_valve_fastest(cleaned_valve)+wait(10)+go_to_absolute_pump_position(0)
    return sequence

def initialize_LSPOne(lsp):
    set_force(lsp, "low")
    print("LSPOne initialized")

##
######################TEST/SEQUENCE FUNCTIONS######################
##



##
######################MAIN######################
##

def filling_pipes(lsp):
    trash = 1
    water = 2
    detergent = 3
    blocking = 4
    cartridge = 5
    sample = 6
    
    fill_water_pipe = change_to_valve_fastest(water)+wait(200)+peak_speed(50)+wait(200)+pickup_position(500)+wait(200)+change_to_valve_fastest(trash)+wait(200)+go_to_absolute_pump_position(0)+wait(200)
    fill_detergent_pipe = change_to_valve_fastest(detergent)+wait(200)+peak_speed(50)+wait(200)+pickup_position(500)+wait(200)+change_to_valve_fastest(trash)+wait(200)+go_to_absolute_pump_position(0)+wait(200)
    fill_blocking_pipe = change_to_valve_fastest(blocking)+wait(200)+peak_speed(50)+wait(200)+pickup_position(200)+wait(200)+change_to_valve_fastest(trash)+wait(200)+go_to_absolute_pump_position(0)+wait(200)
    clean_trash_water = change_to_valve_fastest(water)+wait(200)+peak_speed(500)+wait(200)+pickup_position(2000)+wait(200)+change_to_valve_fastest(trash)+wait(200)+go_to_absolute_pump_position(0)+wait(200)
    clean_trash_air = change_to_valve_fastest(sample)+wait(200)+peak_speed(500)+wait(200)+pickup_position(2000)+wait(200)+change_to_valve_fastest(trash)+wait(200)+go_to_absolute_pump_position(0)+wait(200)

    final_sequence=fill_water_pipe+fill_detergent_pipe+fill_blocking_pipe+clean_trash_water+clean_trash_air

    write_sequence_to_pump(lsp, final_sequence)

def clean_sample_cartridge_trash(lsp):
    trash = 1
    water = 2
    detergent = 3
    blocking = 4
    cartridge = 5
    sample = 6

    fill_detergent=change_to_valve_fastest(detergent)+wait(200)+go_to_absolute_pump_position(3000)+wait(200)
    fill_water=change_to_valve_fastest(water)+wait(200)+go_to_absolute_pump_position(3000)+wait(200)
    clean_sample=change_to_valve_fastest(sample)+wait(200)+dispense_position(1500)+wait(200)
    clean_cartridge=change_to_valve_fastest(cartridge)+wait(200)+dispense_position(1500)+wait(200)
    clean_trash=change_to_valve_fastest(trash)+wait(200)+go_to_absolute_pump_position(0)+wait(200)

    air_cleaning=change_to_valve_fastest(sample)+wait(200)+go_to_absolute_pump_position(1000)+wait(200)+change_to_valve_fastest(cartridge)+wait(200)+go_to_absolute_pump_position(0)+wait(200)+change_to_valve_fastest(trash)+wait(200)+go_to_absolute_pump_position(2000)+wait(200)+change_to_valve_fastest(cartridge)+wait(200)+go_to_absolute_pump_position(0)+wait(200)

    #at the end of this, have the end of 5 on air to aspirate air
    sequence_1=fill_detergent+clean_sample+fill_detergent+clean_cartridge+fill_detergent+clean_trash+fill_water+clean_sample+fill_water+clean_sample+fill_water+clean_trash
    sequence_2=repeat_sequence(air_cleaning,2)

    final_sequence=peak_speed(1000)+sequence_1+peak_speed(500)+sequence_2

    write_sequence_to_pump(lsp, final_sequence)


def clean_all(lsp):
    set_speed=peak_speed(500)

    fill=change_to_valve_fastest(3)+wait(200)+go_to_absolute_pump_position(3000)+wait(200)
    clean_1_2=change_to_valve_fastest(1)+wait(200)+go_to_absolute_pump_position(1500)+wait(200)+change_to_valve_fastest(2)+wait(200)+go_to_absolute_pump_position(0)+wait(200)
    clean_4_5=change_to_valve_fastest(4)+wait(200)+go_to_absolute_pump_position(1500)+wait(200)+change_to_valve_fastest(5)+wait(200)+go_to_absolute_pump_position(0)+wait(200)
    clean_6=change_to_valve_fastest(6)+wait(200)+go_to_absolute_pump_position(0)+wait(200)

    #first bleach, then detergent, then ethanol, then DI water, then air, twice for each step

    sequence_1=fill+clean_1_2+fill+clean_4_5+fill+clean_6
    sequence_2=repeat_sequence(sequence_1,2)+wait(5000)
    sequence_3=repeat_sequence(sequence_2,5)
    final_sequence=set_speed+sequence_3

    write_sequence_to_pump(lsp, final_sequence)

def dispense_blocking_and_sample(lsp):

    bb_incubation_time_ms=20000

    trash = 1
    water = 2
    detergent = 3
    blocking = 4
    cartridge = 5
    sample = 6

    dispense_blocking=change_to_valve_fastest(blocking)+wait(200)+peak_speed(50)+wait(200)+pickup_position(200)+wait(200)+change_to_valve_fastest(cartridge)+wait(200)+peak_speed(20)+wait(200)+go_to_absolute_pump_position(0)+wait(bb_incubation_time_ms)
    add_air = change_to_valve_fastest(trash)+wait(200)+peak_speed(100)+wait(200)+pickup_position(40)+wait(200)+change_to_valve_fastest(cartridge)+wait(200)+go_to_absolute_pump_position(0)+wait(200)
    pickup_sample = change_to_valve_fastest(sample)+wait(200)+peak_speed(10)+wait(200)+pickup_position(80)+wait(200)+change_to_valve_fastest(trash)+wait(200)+go_to_absolute_pump_position(0)+wait(200)+change_to_valve_fastest(sample)+wait(200)+pickup_position(120)+wait(200)
    dispense_sample = change_to_valve_fastest(cartridge)+peak_speed(10)+wait(200)+dispense_position(120)+wait(200)+change_to_valve_fastest(sample)+peak_speed(500)+wait(200)+pickup_position(500)+wait(200)+change_to_valve_fastest(cartridge)+wait(200)+peak_speed(2)+wait(200)+dispense_position(120)+wait(2000)+repeat_sequence(pickup_position(160)+wait(2000)+dispense_position(160)+wait(2000),1)+peak_speed(20)+wait(200)+go_to_absolute_pump_position(0)+wait(200)
    
    final_sequence=dispense_blocking+pickup_sample+dispense_sample

    write_sequence_to_pump(lsp, final_sequence)


def main():
    pump_position = 0

    #lsp = serial.Serial("COM4", 9600, timeout=1000)
    lsp = serial.Serial("/dev/cu.usbserial-P100_OSPM28740", 9600, timeout=1000)
    print('LSPone connected on ',lsp.name)
    #%% Initialise LSPone normally already done
    initialize_LSPOne(lsp)
    print("Test about to begin")
    #lsp.write(b"/1V300M1000O1M1000A3000M1000O2M1000A2400M1000O3M1000A1800M1000O4M1000A1200M1000O5M1000A600M1000O6M1000A0M1000R\r")
    #final_procedure_dispense_sample(lsp)
    #filling_pipes(lsp)
    #clean_sample_cartridge_trash(lsp)
    #dispense_blocking_and_sample(lsp)
    #lsp.write(b"/1V300M1000O1M1000A1000M1000O5M1000A0M1000R\r")
    clean_all(lsp)
    time.sleep(5)