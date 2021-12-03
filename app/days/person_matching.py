import json

import pandas as pd

from app.config.config import Config

scores = {
    'first_name': 5,
    'last_name': 5,
    'full_name': 20,
    'phone_number': 5,
    'email': 5,
    'street_address': 5,
    'city': 5,
    'state': 5,
    'zip_code': 5,
}


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
        self.data = self.get_data()

    def get_data(self):
        return pd.read_csv(f"{Config.DATA_EXAMPLES_PATH}/MOCK_DATA.csv")

    def assign_confidence(self):
        self.data['confidence_score'] = self.data.apply(self.confidence_score, axis=1)
        self.data.sort_values(by='confidence_score',
                              ascending=False,
                              inplace=True)
        data = json.loads(self.data[:3].to_json(orient='index'))
        return data

    def confidence_score(self, row):
        score = 0
        if self.first_name in row.get('first_name'):
            score += 5
            if self.last_name in row.get('last_name'):
                score += 15
        elif self.last_name in row.get('last_name'):
            score += 10
        if self.phone_number in row.get('phone_number'):
            score += 20
        if self.email_address in row.get('email'):
            score += 20

        address_check = 0
        if self.street_address in row.get('address'):
            score += 10
            address_check += 1
        if self.city in row.get('city'):
            score += 10
            address_check += 1
        if self.state in row.get('state'):
            score += 5
            address_check += 1
        # if self.zip_code == row.get('zip'):
        #     score += 5

        if address_check == 3:
            score += 15

        return score


js = ContactMatch(
    FIRSTNAME="Nydia",
    LASTNAME="Hecks",
    PHONENUMBER="216-409-9183",
    EMAILADDRESS="nhecks0@cnet.com",
    STREETADDRESS="69 Harbort Park",
    CITY="Cleveland",
    STATE="Ohio",
    ZIPCODE=""
).assign_confidence()

print(js)