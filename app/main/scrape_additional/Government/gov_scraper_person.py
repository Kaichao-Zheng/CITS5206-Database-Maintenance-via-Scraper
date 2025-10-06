import re
from .constants import AUS_STATES, PREFIXES, SUFFIXES, GENDERS, MALES, FEMALES

class Person:
    def __init__(self):
        self.salutation = None
        self.fname = None
        self.lname = None
        self.name = None
        self.organisation = None
        self.department = None
        self.position = None
        self.gender = None
        self.phone = None
        self.email = None
        self.fax = None
        self.website = None
        self.address = None
        self.postal_address = None
        self.city = None
        self.state = None
        self.country = None

    def addName(self, name):
        self.name = name
        
        # Preprocessing
        name = name.strip()
        name = re.sub(r'\(.*?\)', '', name)
        
        # Save prefix as salutation
        tokens = name.replace(',', ' ').split()
        
        prefix_index = -1
        for i, token in enumerate(tokens):      # Can handle a mix of invalid and valid prefixes at the start
            if token in PREFIXES:               # But cannot handle separated valid salutation at the end
                prefix_index = i                # e.g. The Hon. Peter Mcclellan Justice
        
        if prefix_index >= 0:
            salutation = " ".join(tokens[:prefix_index + 1])
            self.salutation = salutation
            
            # Identify gender
            last_salutation = salutation.split()[-1]        # assume gender salutation is always at the end
            if last_salutation in GENDERS:
                self.addGender(last_salutation)
                
            tokens = tokens[prefix_index + 1:]
        
        # Remove suffixes
        while tokens and tokens[-1].rstrip('-') in SUFFIXES:
            tokens.pop(-1)
        
        # Split fname and lname
        if tokens:
            self.fname = tokens[0]
            self.lname = " ".join(tokens[1:])

    def addOrganisation(self, organisation):
        self.organisation = organisation

    def addDepartment(self, department):
        self.department = department

    def addPosition(self, position):
        self.position = position
        
    def addGender(self, gender):
        if gender in MALES:
            self.gender = "Male"
        elif gender in FEMALES:
            self.gender = "Female"

    def addPhone(self, phone):
        self.phone = phone

    def addEmail(self, email):
        self.email = email

    def addFax(self, fax):
        self.fax = fax

    def addWebsite(self, website):
        self.website = website

    def addAddress(self, address):
        self.address = address

    def addPostalAddress(self, postal_address):
        self.postal_address = postal_address
        
    def addLocation(self, location):
        if not location:
            return
        components = location.split(" ")
        self.state = components[-2]
        if self.state in AUS_STATES:
            self.country = "Australia"
        else:
            self.city = " ".join(components[:-2])