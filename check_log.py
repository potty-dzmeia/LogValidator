import csv

from participant import Participant
from qso import Qso
import glob
from datetime import datetime
import os
import logging
import logging.config
import my_utils
import argparse
import re

# logging.config.fileConfig("logging.conf", disable_existing_loggers=False)
# logger = logging.getLogger(__name__)
# logger.setLevel(level=logging.INFO)


def parseLog(file):
    participant = Participant()

    print("%-25s %s" % ("Parsing log:",file))
    f = open(file, "r", encoding=my_utils.getFileEncoding(file))

    for line in f:
        line_split = line.split()
        try:
            if len(line_split) == 0:
                pass
            elif line_split[0] == "CALLSIGN:":
                participant.callsign = line_split[1].upper()
            elif line_split[0] == "NAME:":
                participant.name = " ".join(line_split[1:])
            elif line_split[0] == "CATEGORY:":
                participant.category = " ".join(line_split[1:])
            elif line_split[0] == "QSO:":
                participant.log.append(Qso(line_split))
        except:
            print("Error in line: " + line)
            pass  # empty line

    if len(participant.callsign):
        print("Success!")
    else:
        print("Error!")

    return participant


def checkLog(participant):

    unique_calls = dict() # will hold {"CallSign": "RCV2", ...}

    for qso in participant.log:
        # Check the RCV exchange with the original
        if qso.his_call in unique_calls:
            if qso.rcv2 != unique_calls[qso.his_call]:
                qso.error_code = Qso.ERROR_RECEIVE
        # New callsign - add to dict
        else:
            unique_calls[qso.his_call] = qso.rcv2


def writeResults(participant, path_to_cabillo):

    directory = os.path.dirname(os.path.abspath(path_to_cabillo))
    filename = os.path.basename(os.path.abspath(path_to_cabillo))

    # Print the results into a CSV file called results.csv
    filename = os.path.join(directory, filename+"_validation.txt")

    call_list = []  # Will hold the already printed

    with open(filename, "w+", encoding="utf-8") as output:
        for qso in participant.log:
            if qso.error_code != Qso.NO_ERROR and qso.his_call not in call_list:
                output.write("Check exchanges with: " + qso.his_call + "\n")
                output.write("-------------------------------------\n")
                call_list.append(qso.his_call)
                output.write(participant.print_all_qsos(qso.his_call))
                output.write('\n')

        print("%-25s %s" % ("Results in file:", filename))

def main(path_to_cabillo):

    # Parse the logs
    participant = parseLog(path_to_cabillo)
    # Check the logs
    checkLog(participant)
    #
    writeResults(participant, path_to_cabillo)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Program validating yor log for consistent RCV exchange. Written by LZ1ABC.')
    parser.add_argument("path", help="Complete path to the cabrillo formatted log that you want to check. Example: \"C:\logs\mylog.cab\"")
    args = parser.parse_args()

    main(os.path.abspath(args.path))

    # main(os.path.abspath(r'C:\Users\levkov_cha_ext\Documents\N1MM Logger+\ExportFiles\iaru_test.log'))

