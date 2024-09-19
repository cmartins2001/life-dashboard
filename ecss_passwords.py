'''
Random password generator
Works with a list of names
'''

import random as rd
import string

# List of names:
ECSS_members = ["Connor", "Elita", "Leana", "Laura", "Piper"]
PASSWORD_LENGTH = 51


# Function that generates a password based on a username and specified length:
def get_pw(prefix, pw_length):

    # Initialize the string:
    pw = prefix

    for i in range(0,pw_length):

        if i % 2 != 0:
            i = rd.randint(0,9)

        else:
            i = rd.choice(string.ascii_letters)
    
        pw = f'{pw}{i}'

    return pw


# Function that converts list of names into password prefixes:
def convert_names(name_list):

    # List comprehension:
    pw_prefixes = [(name.replace(name[0], name[0].lower(),1) + "-") for name in name_list]

    return pw_prefixes

# Convert to password prefixes:
prefixes = convert_names(ECSS_members)

# List of passwords:
passwords = [get_pw(prefix, PASSWORD_LENGTH) for prefix in prefixes]

# Make a dictionary:
pw_dict = {name : pw for (name, pw) in zip(ECSS_members, passwords)}

# Print the output:
for key, val in pw_dict.items():

    print(f'\n{key}:\t\t{val}\n')
