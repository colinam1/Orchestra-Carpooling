import gspread

service_account = gspread.service_account()
sheet = service_account.open("Fall 2021 Second Concert Orchestras Carpool Survey (Responses)")
response_worksheet = sheet.worksheet("Form Responses 1")

all_orchestras_info = response_worksheet.get_all_records()
all_philharmonic_info = sheet.add_worksheet(title="All Philharmonic", rows="100", cols="20")
all_symphony_info = sheet.add_worksheet(title="All Symphony", rows="100", cols="20")
all_string_info = sheet.add_worksheet(title="All String", rows="100", cols="20")

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