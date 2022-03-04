import gspread as gs
import math as mt
import random as rn
import numpy as np
import copy as cp
import re

class driver:
    def __init__(self, google_sheet_response):
        self.contact_info = [google_sheet_response[1], google_sheet_response[3], google_sheet_response[4], google_sheet_response[5], 'Driver', True]
        self.remaining_seats = google_sheet_response[-2]
        self.riders = []
        if (re.search('no', google_sheet_response[7], re.IGNORECASE) and re.search('cello', google_sheet_response[7], re.IGNORECASE)) or (re.search('no', google_sheet_response[9], re.IGNORECASE) and re.search('cello', google_sheet_response[9], re.IGNORECASE)):
            self.no_cello_space = True
        else:
            self.no_cello_space = False
    
    def add_rider(self, rider_instance):
        if self.remaining_seats < rider_instance.seat_value:
            return "Rider not added."
        else:
            self.riders.append(rider_instance)
            rider_instance.contact_info[-1] = True
            self.remaining_seats -= rider_instance.seat_value
            return "Rider added."
                
class rider:
    def __init__(self, google_sheet_response):
        self.contact_info = [google_sheet_response[1], google_sheet_response[3], google_sheet_response[4], google_sheet_response[5], 'Passenger', False]
        if self.contact_info[1] == 'Cello':
            self.seat_value = 2
        else:
            self.seat_value = 1
            
def create_assignments(driver_object_list, rider_object_list):
    # Assigning each rider to each driver
    best_driver_object_list = []
    # Arbitrarily large number
    best_remaining_riders = 1000
    for iteration in range(1):
        temp_driver_object_list = cp.deepcopy(driver_object_list)
        temp_rider_object_list = cp.deepcopy(rider_object_list)
        for driver_instance in temp_driver_object_list:
            for rider_instance in temp_rider_object_list:
                # Skip this instance of the rider if the rider is a cello and the driver said no cellos will fit
                if driver_instance.no_cello_space and rider_instance.contact_info[1] == 'Cello':
                    continue
                
                # Try to add rider
                add_rider_response = driver_instance.add_rider(rider_instance)
                
                # Too few seats available to add cello player, move to next rider to see if they are not a cello
                if add_rider_response == "Rider not Added." and driver_instance.remaining_seats > 0:
                    continue
                
                # Remove the rider from the active list of riders if seat is assigned to them
                temp_rider_object_list.remove(rider_instance)
                
                # Skip to next driver if the driver has no remaining seats
                if driver_instance.remaining_seats == 0:
                    break
            # End function if all riders have been assigned    
            if temp_rider_object_list == []:
                # Save finalized assignments where everyone has a ride, otherwise keep searching
                best_driver_object_list = cp.deepcopy(temp_driver_object_list)
                remaining_riders_list = []
                best_remaining_riders = 0
                return best_remaining_riders, best_driver_object_list, remaining_riders_list
        remaining_riders = len(temp_rider_object_list)
        if remaining_riders < best_remaining_riders:
            best_driver_object_list = cp.deepcopy(temp_driver_object_list)
            remaining_riders_list = cp.deepcopy(temp_rider_object_list)
            best_remaining_riders = remaining_riders
        rn.shuffle(rider_object_list)
    return best_remaining_riders, best_driver_object_list, remaining_riders_list

def create_assignments_2(driver_object_list, rider_object_list):
    
    # Arbitrarily large number to start
    best_remaining_riders = 1000
    
    for iteration in range(1):
        temp_driver_object_list = cp.deepcopy(driver_object_list)
        temp_rider_object_list = cp.deepcopy(rider_object_list)
        for driver_instance in temp_driver_object_list:
            for rider_instance in temp_rider_object_list:
                # Skip rider if they already have ride
                if rider_instance.contact_info[-1]:
                    continue
                
                # Skip this instance of the rider if the rider is a cello and the driver said no cellos will fit
                if driver_instance.no_cello_space and rider_instance.contact_info[1] == 'Cello':
                    continue
                    
                # Try to add rider
                add_rider_response = driver_instance.add_rider(rider_instance)
                
                # Too few seats available to add cello player, move to next rider to see if they are not a cello
                if add_rider_response == "Rider not Added.":
                    continue        
        remaining_riders_list = [rider_instance for rider_instance in temp_rider_object_list if not rider_instance.contact_info[-1]]
        if len(remaining_riders_list) == 0:
            best_assignments_list = cp.deepcopy(temp_driver_object_list)
            best_remaining_riders = 0
            best_remaining_riders_list = []
            break
        elif len(remaining_riders_list) < best_remaining_riders:
            best_remaining_riders = len(remaining_riders_list)
            best_remaining_riders_list = cp.deepcopy(remaining_riders_list)
            best_assignments_list = cp.deepcopy(temp_driver_object_list)
        else:
            pass
        rn.shuffle(rider_object_list)
    return best_remaining_riders, best_assignments_list, best_remaining_riders_list

def output_assignments(driver_object_list, remaining_riders_list):
    assignment_list = []
    for driver_instance in driver_object_list:
        assignment_list.append(driver_instance.contact_info[0:-1])
        for rider_instance in driver_instance.riders:
            assignment_list.append(rider_instance.contact_info[0:-1])
    assignment_list.append(5*['Remaining'])
    for rider_instance in remaining_riders_list:
        assignment_list.append(rider_instance.contact_info[0:-1])
    return assignment_list

def check_assignments(assignments_list, rider_instance):
    for driver_instance in assignments_list:
        for assigned_rider in driver_instance.riders:
            match = rider_instance.contact_info[0] == assigned_rider.contact_info[0]
            if match:
                return True
    return False

def check_remainder(remaining_list, rider_instance):
    for remaining_rider in remaining_list:
        match = rider_instance.contact_info[0] == remaining_rider.contact_info[0]
        if match:
            return True
    return False

def find_unaccounted(assignments_list, remaining_list, rider_list):
    unaccounted_list = []
    for rider_instance in rider_list:
        match_assigned = check_assignments(assignments_list, rider_instance)
        match_remaining = check_remainder(remaining_list, rider_instance)
        if not match_assigned and not match_remaining:
            unaccounted_list.append(rider_instance)
    return unaccounted_list

if __name__ == "__main__":
    service_account = gs.service_account()
    sheet = service_account.open("Spring 2022 First Concert Orchestras Carpool Survey (Responses)")
    response_worksheet = sheet.worksheet("Form Responses 1")

    all_orchestras_info = response_worksheet.get_all_records()

    try:
        worksheet = sheet.worksheet("Philharmonic Assignments")
        sheet.del_worksheet(worksheet)
    except:
        pass
    
    philharmonic_assignments = sheet.add_worksheet(title="Philharmonic Assignments", rows="100", cols="20")
        
    try:
        worksheet = sheet.worksheet("Symphony Assignments")
        sheet.del_worksheet(worksheet)
    except:
        pass

    symphony_assignments = sheet.add_worksheet(title="Symphony Assignments", rows="100", cols="20")
    
    try:
        worksheet = sheet.worksheet("String Assignments")
        sheet.del_worksheet(worksheet)
    except:
        pass
    
    string_assignments = sheet.add_worksheet(title="String Assignments", rows="100", cols="20")

    philharmonic_riders = []
    symphony_riders = []
    string_riders = []

    philharmonic_drivers = []
    symphony_drivers = []
    string_drivers = []

    philharmonic_driver_object_list = []
    symphony_driver_object_list = []
    string_driver_object_list = []
    
    philharmonic_rider_object_list = []
    symphony_rider_object_list = []
    string_rider_object_list = []
    
    philharmonic = []
    symphony = []
    string = []

    # Separating into lists of info for drivers and riders for each orchestra 
    for response in all_orchestras_info:
        response_list = list(response.values())
        if response_list[2] == 'Philharmonic Orchestra':
            philharmonic.append(response_list)
        elif response_list[2] == 'Symphony Orchestra':
            symphony.append(response_list)
        elif response_list[2] == 'String Orchestra':
            string.append(response_list)
            
    for philharmonic_member in philharmonic:
        if philharmonic_member[6] == 'Willing to provide ride':
            philharmonic_drivers.append(philharmonic_member)
        elif philharmonic_member[6] == 'Need ride':
            philharmonic_riders.append(philharmonic_member)
            
    for symphony_member in symphony:
        if symphony_member[6] == 'Willing to provide ride':
            symphony_drivers.append(symphony_member)
        elif symphony_member[6] == 'Need ride':
            symphony_riders.append(symphony_member)
    
    for string_member in string:
        if string_member[6] == 'Willing to provide ride':
            string_drivers.append(string_member)
        elif string_member[6] == 'Need ride':
            string_riders.append(string_member)
            
    # Setting lists of info as lists of rider and driver objects    
    for philharmonic_driver in philharmonic_drivers:
        philharmonic_driver_object_list.append(driver(philharmonic_driver))
        
    for philharmonic_rider in philharmonic_riders:
        philharmonic_rider_object_list.append(rider(philharmonic_rider))
        
    for symphony_driver in symphony_drivers:
        symphony_driver_object_list.append(driver(symphony_driver))
        
    for symphony_rider in symphony_riders:
        symphony_rider_object_list.append(rider(symphony_rider))
        
    for string_driver in string_drivers:
        string_driver_object_list.append(driver(string_driver))
        
    for string_rider in string_riders:
        string_rider_object_list.append(rider(string_rider))
    
    philharmonic_remainder, best_philharmonic_assignments, remaining_riders_philharmonic = create_assignments_2(philharmonic_driver_object_list, philharmonic_rider_object_list)
    symphony_remainder, best_symphony_assignments, remaining_riders_symphony = create_assignments_2(symphony_driver_object_list, symphony_rider_object_list)
    string_remainder, best_string_assignments, remaining_riders_string = create_assignments_2(string_driver_object_list, string_rider_object_list)
    
    unaccounted_philharmonic = find_unaccounted(best_philharmonic_assignments, remaining_riders_philharmonic, philharmonic_rider_object_list)
    unaccounted_symphony = find_unaccounted(best_symphony_assignments, remaining_riders_symphony, symphony_rider_object_list)
    unaccounted_string = find_unaccounted(best_string_assignments, remaining_riders_string, string_rider_object_list)
    
    # Need to use numpy array or else Google gets mad when updating the sheets
    philharmonic_assignments_list = np.array(output_assignments(best_philharmonic_assignments, remaining_riders_philharmonic))
    symphony_assignments_list = np.array(output_assignments(best_symphony_assignments, remaining_riders_symphony))
    string_assignments_list = np.array(output_assignments(best_string_assignments, remaining_riders_string))
    
    philharmonic_assignments.update('A1', philharmonic_assignments_list.tolist())
    symphony_assignments.update('A1', symphony_assignments_list.tolist())
    string_assignments.update('A1', string_assignments_list.tolist())
            