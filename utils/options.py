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

# diagnosis_options = set()
# bodyPart_options = set()
# tissuetype_options = set()
# pathologytype_options = set()

# for row in OSIICS_data:
#     Diagnosis_options.add(row["OSIICS_Diagnosis"])
#     bodyPart_options.add(row["OSIICS_BodyPart"])
#     tissuetype_options.add(row["OSIICS_TissueType"])
#     pathologytype_options.add(row["OSIICS_PathologyType"])