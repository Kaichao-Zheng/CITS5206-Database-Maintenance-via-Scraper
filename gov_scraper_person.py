class Person:
    def __init__(self):
        self.name = None
        self.organisation = None
        self.department = None
        self.position = None
        self.phone = None
        self.email = None
        self.fax = None
        self.website = None
        self.address = None
        self.postal_address = None

    def addName(self, name):
        self.name = name

    def addOrganisation(self, organisation):
        self.organisation = organisation

    def addDepartment(self, department):
        self.department = department

    def addPosition(self, position):
        self.position = position

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

