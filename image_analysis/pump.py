"""
pump.py
~~~~~~~~~~~~~~~~~
This program shows how to connect to to the LSPone (laboratory syringe pump) using python and do the General cleaning procedure.
It should be done at the beginning and end of the day.
:author: SenSwiss 2021

Cleaning procedure: 
Do the steps 2x using 1% chlorine bleach and deionized water
Do the steps 2x using detergent
Do the steps 1x using 70% ethanol
Do the steps 2x using PBS
Do the steps 2x with air
"""

# include python libraries
import sys
import serial
import time

#%% Functions
def initialise_LSPone(lsp):
    #Initialise LSPone
    lsp.write(b"/1Z3R\r")
    time.sleep(20)
    print("LSP one ready")

def general_cleaning_procedure(lsp):
    # 2: PBS, 3: Air, 4: Ethanol
        lsp.write(b"/1V200M200B2M1000A1500M1000B6M1000A0M1000B3M1000A1500M1000B6M1000A0M1000B4M1000A1500M1000B6M1000A0M1000B3M1000A3000M1000B6M1000A0M1000B3M1000A3000M1000B6M1000A0M1000R\r")


def pick_BB(lsp):
    lsp.write(b"/1V5M200B6M1000A480M1000V300M200B3M1000A510M1000B6M1000V5M200R\r")

def push_pull_sample(lsp, n_times):
    if n_times == 1:
        lsp.write(b"/1V5M1000A660M1000A510M1000R\r")
    elif n_times == 2:
        lsp.write(b"/1V5M1000A660M1000A510M1000A660M1000A510M1000R\r")
    elif n_times == 3:
        lsp.write(b"/1V5M1000A660M1000A510M1000A660M1000A510M1000A660M1000A510M1000R\r")
    elif n_times == 4:
        lsp.write(b"/1V5M1000A660M1000A510M1000A660M1000A510M1000A660M1000A510M1000A660M1000A510M1000R\r")


def general_cleaning_procedure_fast(lsp):
    start_s = b"/1V300M200" #start with speed 3000 ul/min
    pull = b"M1000A1500M1000"
    push = b"B6M1000A0M1000"
    end_s = b"R\r"
    lsp.write(start_s + b"B2" + pull + push + b"B3" + pull + push + b"B4" + pull + push + end_s)


    # Push pull sample for 69s each
def push_pull_sample_n_times(lsp,n):
    start_s = b"/1V5M1000B6M1000"
    push_pull = b"A660M1000A510M1000"
    end_s = b"R\r"
    lsp.write(start_s+n*push_pull+end_s)


def air_cleaning(lsp):
    lsp.write(b"/1V300B3M1000A1000M1000B6M1000A0M1000R\r")


def pick_BB_again(lsp):
    # IN CASE BB IS NOT MOVING
    # Start picking BB again at 100 ul/min
    #Empty syringe
    lsp.write(b"/1V150B1M1000A0M1000RV10M200B6M1000A480M1000R\r")

