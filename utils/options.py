def create_options(Name: str, x_ID: str):
    return Name + " (ID: " + str(x_ID) + ")"

def create_list_options(data, table):
    options = []
    x = None
    y = None

    if table == "Player":
        x = "PlayerName"
        y = "PlayerID"
    
    if table == "OSIICS":
        x = "OSIICS_Diagnosis"
        y = "OSIICS_ID"

    for row in data:
        details = create_options(row[x], row[y])
        options.append(details)

    return options