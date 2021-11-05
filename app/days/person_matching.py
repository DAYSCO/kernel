class ContactMatch:

    def __init__(self, *args, **kwargs):
        self.first_name = kwargs.get('FIRSTNAME', '')
        self.last_name = kwargs.get('LASTNAME', '')
        self.phone_number = kwargs.get('PHONENUMBER', '')
        self.email_address = kwargs.get('EMAILADDRESS', '')
        self.street_address = kwargs.get('STREETADDRESS', '')
        self.city = kwargs.get('CITY', '')
        self.state = kwargs.get('STATE', '')
        self.zip_code = kwargs.get('ZIPCODE', '')
        self.full_address = kwargs.get('FULLADDRESS', '')

    def get_data(self):
        pass

    def assign_confidence(self):
        pass
