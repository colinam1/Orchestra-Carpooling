import gspread as gs
import math as mt
import random as rn
import numpy as np
import copy as cp

class driver:
    def __init__(self, google_sheet_response):
        self.contact_info = [google_sheet_response[1], google_sheet_response[3], google_sheet_response[4], google_sheet_response[5], 'Driver']
        self.remaining_seats = google_sheet_response[-2]
        self.riders = []
        self.remaining_cellos = mt.floor(google_sheet_response[-2]/2)
    
    def add_rider(self, rider_instance):
        if self.remaining_seats < rider_instance.seat_value:
            return "Rider not added."
        else:
            self.riders.append(rider_instance)
            self.remaining_seats -= rider_instance.seat_value
                
class rider:
    def __init__(self, google_sheet_response):
        self.contact_info = [google_sheet_response[1], google_sheet_response[3], google_sheet_response[4], google_sheet_response[5], 'Passenger']
        if self.contact_info[1] == 'Cello':
            self.seat_value = 2
        else:
            self.seat_value = 1
            
def create_assignments(driver_object_list, rider_object_list):
    # Assigning each rider to each driver
    best_driver_object_list = []
    # Arbitrarily large number
    best_remaining_riders = 1000
    for iteration in range(10000):
        temp_driver_object_list = cp.deepcopy(driver_object_list)
        temp_rider_object_list = cp.deepcopy(rider_object_list)
        for driver_instance in temp_driver_object_list:
            for rider_instance in temp_rider_object_list:
                add_rider_response = driver_instance.add_rider(rider_instance)
                
                if add_rider_response == "Rider not Added." and driver_instance.remaining_seats > 0:
                    continue
                
                temp_rider_object_list.remove(rider_instance)
                
                if driver_instance.remaining_seats == 0:
                    break
            if temp_rider_object_list == []:
                # Save finalized assignments where everyone has a ride, otherwise keep searching
                driver_object_list = cp.deepcopy(temp_driver_object_list)
                return 0
        remaining_riders = len(temp_rider_object_list)
        if remaining_riders < best_remaining_riders:
            best_driver_object_list = cp.deepcopy(temp_driver_object_list)
            best_remaining_riders = remaining_riders
        rn.shuffle(rider_object_list)
    return best_remaining_riders, best_driver_object_list
    

def output_assignments(driver_object_list):
    assignment_list = []
    for driver_instance in driver_object_list:
        assignment_list.append(driver_instance.contact_info)
        for rider_instance in driver_instance.riders:
            assignment_list.append(rider_instance.contact_info)
    return assignment_list
            
if __name__ == "__main__":
    service_account = gs.service_account()
    sheet = service_account.open("Fall 2021 Second Concert Orchestras Carpool Survey (Responses)")
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

    # Separating into lists of info for drivers and riders for each orchestra 
    for response in all_orchestras_info:
        response_list = list(response.values())
        if response_list[2] == 'Philharmonic Orchestra':
            if response_list[6] == 'Need ride':
                philharmonic_riders.append(list(response.values()))
            elif response_list[6] == 'Willing to provide ride':
                philharmonic_drivers.append(list(response.values()))
            else:
                pass
        elif response_list[2] == 'Symphony Orchestra':
            if response_list[6] == 'Need ride':
                symphony_riders.append(list(response.values()))
            elif response_list[6] == 'Willing to provide ride':
                symphony_drivers.append(list(response.values()))
            else:
                pass
        else:
            if response_list[6] == 'Need ride':
                string_riders.append(list(response.values()))
            elif response_list[6] == 'Willing to provide ride':
                string_drivers.append(list(response.values()))
            else:
                pass
    
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
    
    philharmonic_remainder, best_philharmonic_assignments = create_assignments(philharmonic_driver_object_list, philharmonic_rider_object_list)
    symphony_remainder, best_symphony_assignments = create_assignments(symphony_driver_object_list, symphony_rider_object_list)
    string_remainder, best_string_assignments = create_assignments(string_driver_object_list, string_rider_object_list)
    
    # Need to use numpy array or else Google gets mad when updating the sheets
    philharmonic_assignments_list = np.array(output_assignments(best_philharmonic_assignments))
    symphony_assignments_list = np.array(output_assignments(best_symphony_assignments))
    string_assignments_list = np.array(output_assignments(best_string_assignments))
    
    philharmonic_assignments.update('A1', philharmonic_assignments_list.tolist())
    symphony_assignments.update('A1', symphony_assignments_list.tolist())
    string_assignments.update('A1', string_assignments_list.tolist())
            