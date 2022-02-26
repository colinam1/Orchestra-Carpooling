import gspread

service_account = gspread.service_account()
sheet = service_account.open("Fall 2021 Second Concert Orchestras Carpool Survey (Responses)")
response_worksheet = sheet.worksheet("Form Responses 1")

all_orchestras_info = response_worksheet.get_all_records()

philharmonic_assignments = sheet.add_worksheet(title="Philharmonic Assignments", rows="100", cols="20")
symphony_assignments = sheet.add_worksheet(title="Symphony Assignments", rows="100", cols="20")
string_assignments = sheet.add_worksheet(title="String Assignments", rows="100", cols="20")

philharmonic_riders = []
symphony_riders = []
string_riders = []

philharmonic_drivers = []
symphony_drivers = []
string_drivers = []

# Separating into lists of info for drivers and riders for each orchestra 
for response in all_orchestras_info:
    response_list = list(response)
    if response_list[2] == 'Philharmonic Orchestra':
        if response_list[6] == 'Need ride':
            philharmonic_riders.append(response)
        elif response_list[6] == 'Willing to provide ride':
            philharmonic_drivers.append(response)
        else:
            pass
    elif response_list[2] == 'Symphony Orchestra':
        if response_list[6] == 'Need ride':
            symphony_riders.append(response)
        elif response_list[6] == 'Willing to provide ride':
            symphony_drivers.append(response)
        else:
            pass
    else:
        if response_list[6] == 'Need ride':
            string_riders.append(response)
        elif response_list[6] == 'Willing to provide ride':
            string_drivers.append(response)
        else:
            pass
        
class driver:
    def __init__(self, google_sheet_response):
        self.contact_info = [google_sheet_response[1], google_sheet_response[3], google_sheet_response[4], google_sheet_response[5]]
        self.remaining_seats = google_sheet_response[-2]
        self.riders = []
    
    def add_rider(self, rider_instance):
        if self.remaining_seats < rider_instance.seat_value:
            return
        else:
            self.riders.append(rider_instance)
            self.remaining_seats -= rider_instance.seat_value
            
         
class rider:
    def __init__(self, google_sheet_response):
        self.contact_info = self.contact_info = [google_sheet_response[1], google_sheet_response[3], google_sheet_response[4], google_sheet_response[5]]
        if self.contact_info[1] == 'Cello':
            self.seat_value = 2
        else:
            self.seat_value = 1
            