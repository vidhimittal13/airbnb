import pandas as pd
from shapely.wkt import loads

#Read-in data
NY_arrests = pd.read_csv("NYPD_Arrests.csv")

#remove duplicates
NY_arrests = NY_arrests.drop_duplicates()

#subset of dataset needed
NY_arrests = NY_arrests[["ARREST_KEY", "ARREST_DATE", "PD_CD", "OFNS_DESC", "Latitude", "ARREST_BORO", "Longitude", "Lon_Lat"]]

#remove missing entries
NY_arrests = NY_arrests.dropna(subset=["ARREST_KEY", "ARREST_DATE", "PD_CD", "OFNS_DESC", "ARREST_BORO", "Latitude", "Longitude", "Lon_Lat"])

#include arrests only 2018 and after
NY_arrests["ARREST_DATE"] = pd.to_datetime(NY_arrests["ARREST_DATE"], format="%m/%d/%Y")
NY_arrests = NY_arrests[NY_arrests["ARREST_DATE"].dt.year >= 2020]

#set bounds of NYC (same for listings.csv)
north = 40.92
south = 40.4
east = -73.6
west = -74

#filter out arrests outside this bound 
NY_arrests = NY_arrests[(NY_arrests['Latitude'] >= south) 
            & (NY_arrests['Latitude'] <= north) 
            & (NY_arrests['Longitude'] >= west) 
            & (NY_arrests['Longitude'] <= east)]

#print(NY_arrests['OFNS_DESC'].unique())

remove_offs = {
    'MISCELLANEOUS PENAL LAW',
    'OFFENSES AGAINST PUBLIC ADMINI', 
    'JOSTLING',
    'VEHICLE AND TRAFFIC LAWS',
    'FOR OTHER AUTHORITIES',
    'NYS LAWS-UNCLASSIFIED FELONY',
    'OTHER OFFENSES RELATED TO THEF',
    'OFF. AGNST PUB ORD SENSBLTY &',
    '"BURGLAR\'S TOOLS"',
    'OTHER STATE LAWS (NON PENAL LA',
    'OTHER STATE LAWS',
    'ADMINISTRATIVE CODE',
    'AGRICULTURE & MRKTS LAW-UNCLASSIFIED',
    'OFFENSES AGAINST THE PERSON',
    'OTHER STATE LAWS (NON PENAL LAW)',
    'ENDAN WELFARE INCOMP',
    'PARKING OFFENSES',
    '(null)',
    'NYS LAWS-UNCLASSIFIED VIOLATION'
}

NY_arrests = NY_arrests[~NY_arrests['OFNS_DESC'].isin(remove_offs)]


NY_arrests = NY_arrests.replace({'HARRASSMENT 2': 'HARASSMENT', 
                'ESCAPE 3': 'ESCAPE',
                'ASSAULT 3 & RELATED OFFENSES': 'ASSAULT & RELATED OFFENSES',
                'CRIMINAL MISCHIEF & RELATED OF': 'CRIMINAL MISCHIEF',
                'OFF. AGNST PUB ORD SENSBLTY &': 'OFFENSES AGAINST PUBLIC ORDER/ADMINISTRATION',
                'OTHER STATE LAWS (NON PENAL LA': 'OTHER STATE LAWS (NON PENAL LAW)',
                'ENDAN WELFARE INCOMP': 'ENDANGERING WELFARE OF INCOMPETENT',
                'AGRICULTURE & MRKTS LAW-UNCLASSIFIED': 'AGRICULTURE & MARKETS LAW',
                'DISRUPTION OF A RELIGIOUS SERV': 'DISRUPTION OF A RELIGIOUS SERVICE',
                'LOITERING/GAMBLING (CARDS, DIC': 'GAMBLING',
                'OFFENSES AGAINST MARRIAGE UNCL': 'OFFENSES AGAINST MARRIAGE',
                'HOMICIDE-NEGLIGENT,UNCLASSIFIE': 'HOMICIDE-NEGLIGENT'})

def create_point(row):
    return (row['Latitude'], row['Longitude'])

# Apply function to create tuple column
NY_arrests['Lat-Lon'] = NY_arrests.apply(create_point, axis=1)

a_level_offenses = ["SEX CRIMES", "MURDER & NON-NEGL. MANSLAUGHTE", "RAPE", "KIDNAPPING & RELATED OFFENSES", "KIDNAPPING", "FELONY SEX CRIMES"]
b_level_offenses = ["ASSAULT & RELATED OFFENSES", "DANGEROUS WEAPONS", "FELONY ASSAULT", "DANGEROUS DRUGS", "CHILD ABANDONMENT/NON SUPPORT", "OFFENSES RELATED TO CHILDREN"]
c_level_offenses = ["GRAND LARCENY", "ROBBERY", "GRAND LARCENY OF MOTOR VEHICLE", "THEFT-FRAUD", "ARSON", "OFFENSES AGAINST PUBLIC SAFETY", "HOMICIDE-NEGLIGENT-VEHICLE", "HOMICIDE-NEGLIGENT", "ESCAPE", "UNLAWFUL POSS. WEAP. ON SCHOOL"]
d_level_offenses = ["CRIMINAL MISCHIEF", "BURGLARY", "OFFENSES INVOLVING FRAUD", "POSSESSION OF STOLEN PROPERTY", "FRAUDS", "HARASSMENT", "CANNABIS RELATED OFFENSES", "MOVING INFRACTIONS"]
e_level_offenses = ["PETIT LARCENY", "FORGERY", "INTOXICATED & IMPAIRED DRIVING", "CRIMINAL TRESPASS", "OTHER TRAFFIC INFRACTION", "BURGLAR'S TOOLS", "UNAUTHORIZED USE OF A VEHICLE", "INTOXICATED/IMPAIRED DRIVING", "PROSTITUTION & RELATED OFFENSES", "GAMBLING", "ALCOHOLIC BEVERAGE CONTROL LAW", "THEFT OF SERVICES", "ANTICIPATORY OFFENSES", "FRAUDULENT ACCOSTING", "DISORDERLY CONDUCT", "NEW YORK CITY HEALTH CODE", "ADMINISTRATIVE CODES", "DISRUPTION OF A RELIGIOUS SERVICE"]

def categorize_offenses(crime):

    if crime in a_level_offenses:
        return 5
    elif crime in b_level_offenses:
        return 4
    elif crime in c_level_offenses:
        return 3
    elif crime in d_level_offenses:
        return 2
    else:
        return 1

NY_arrests["offense_level"] = NY_arrests["OFNS_DESC"].apply(categorize_offenses)

def calculate_weight(timestamp):
    # Calculate the number of days elapsed since the crime occurred
    days_elapsed = (pd.Timestamp.now() - timestamp).days
    
    # Calculate the weight based on the time elapsed
    max_days = (pd.Timestamp('2023-04-23') - pd.Timestamp('2020-01-01')).days  # Max number of days in the dataset
    weight = days_elapsed / max_days  # Ensure weight is at least 1
    
    return weight

# Calculate the weight for each crime incident
NY_arrests['weight'] = NY_arrests['ARREST_DATE'].apply(calculate_weight)

# Calculate the weighted offense level for each crime incident
NY_arrests['weighted_offense_level'] = NY_arrests['offense_level'] * NY_arrests['weight']

# Group by listing and calculate the weighted average offense level for each listing

NY_arrests.to_csv("NY_arrests.csv")
