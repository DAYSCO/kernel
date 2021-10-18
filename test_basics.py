import json as _json
# import re
import unittest
from pprint import pprint
from app import app


class BasicTests(unittest.TestCase):
    def setUp(self):
        self.test_id = "9a5f0cb0-5443-4aa4-bc10-8bf0d4e15cd9"
        self.app = app.test_client()
        self.maxDiff = None
        self.assertEqual(app.debug, False)
        with open("tests/test_payload.json", "r") as open_f:
            self.config = _json.load(open_f)

    def tearDown(self):
        pass

    def test_1a_upload_excel_file(self):
        headers = {
            "id": "4b6g0db3-4185-3er0-ad95-4tr6j1g36op7",
            "size": "702",
            "name": "MOCK_DATA.xlsx",
            "Content-Type": "multipart/form-data"
        }
        payload = dict()
        payload['file'] = (open('examples/MOCK_DATA.xlsx', 'rb'),
                           'MOCK_DATA.xlsx')
        response = self.app.post('/api/v1/upload-file', headers=headers,
                                 data=payload)
        self.assertEqual(response.status_code, 200)

    def test_1b_read_file_contents(self):
        headers = {
            "id": self.test_id,
            "size": "702",
            "name": "test_file.csv"
        }
        with open('tests/test_file.csv') as test_file:
            contents = test_file.read()
        response = self.app.post('/api/v1/read-file-contents',
                                 headers=headers, data=contents)
        self.assertEqual(response.status_code, 200)

    def test_2_concatenate(self):
        headers = {
            "Content-Type": "application/json",
            "id": self.test_id
        }
        json = self.config['test_2_concatenate']['payload']
        response = self.app.put('/api/v1/column/action',
                                headers=headers, json=json)
        self.assertEqual(response.status_code, 200)

    def test_3_change_type(self):
        headers = {
            "Content-Type": "application/json",
            "id": self.test_id
        }
        json = self.config['test_3_change_type']['payload']
        response = self.app.put('/api/v1/column/action',
                                headers=headers, json=json)
        self.assertEqual(response.status_code, 200)

    def test_4_validate(self):
        headers = {
            "Content-Type": "application/json",
            "id": self.test_id
        }
        json = self.config['test_4_validate']['payload']
        response = self.app.put('/api/v1/column/action',
                                headers=headers, json=json)
        self.assertEqual(response.status_code, 200)

    def test_5_rename(self):
        headers = {
            "Content-Type": "application/json",
            "id": self.test_id
        }
        json = self.config['test_5_rename']['payload']
        response = self.app.put('/api/v1/column/action',
                                headers=headers, json=json)
        self.assertEqual(response.status_code, 200)

    def test_6_remove(self):
        headers = {
            "Content-Type": "application/json",
            "id": self.test_id
        }
        json = self.config['test_6_remove']['payload']
        response = self.app.put('/api/v1/column/action',
                                headers=headers, json=json)
        self.assertEqual(response.status_code, 200)

    def test_7a_substitute(self):
        headers = {
            "Content-Type": "application/json",
            "id": self.test_id
        }
        json = self.config['test_7a_substitute']['payload']
        response = self.app.put('/api/v1/column/action',
                                headers=headers, json=json)
        response = self.app.put('/api/v1/column/action',
                                headers=headers, json=json)
        response = self.app.put('/api/v1/column/action',
                                headers=headers, json=json)
        self.assertEqual(response.status_code, 200)

    def test_7b_substitute(self):
        headers = {
            "Content-Type": "application/json",
            "id": self.test_id
        }
        json = self.config['test_7b_update_value']['payload']
        response = self.app.put('/api/v1/column/action',
                                headers=headers, json=json)
        self.assertEqual(response.status_code, 200)

    def test_80_uppercase(self):
        headers = {
            "Content-Type": "application/json",
            "id": self.test_id
        }
        json = self.config['test_8_uppercase']['payload']
        response = self.app.put('/api/v1/column/action',
                                headers=headers, json=json)
        self.assertEqual(response.status_code, 200)

    def test_81_undo(self):
        headers = {
            "id": self.test_id
        }
        response = self.app.put('/api/v1/table/undo', headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_90_change_date_format(self):
        headers = {
            "Content-Type": "application/json",
            "id": self.test_id
        }
        json = self.config['test_90_change_date_format']['payload']
        response = self.app.put('/api/v1/column/action',
                                headers=headers, json=json)
        self.assertEqual(response.status_code, 200)

    def test_91_get_schema(self):
        headers = {
            "id": self.test_id
        }
        response = self.app.get('/api/v1/table/info', headers=headers)
        # self.assertEqual(response.json,
        #                  self.config['test_91_get_schema']['check_result'])
        self.assertEqual(response.status_code, 200)

    def test_92_get_data(self):
        headers = {
            "Content-Type": "application/json",
            "id": self.test_id
        }
        json = self.config['test_92_get_data']['payload']
        response = self.app.post('/api/v1/table/data',
                                 headers=headers, json=json)
        print()
        pprint(_json.loads(response.data.decode("utf-8")))
        print()
        self.assertEqual(_json.loads(response.data.decode("utf-8")),
                         self.config['test_92_get_data']['check_result'])
        self.assertEqual(response.status_code, 200)

    def test_93_export(self):
        headers = {
            "Content-Type": "application/json",
            "id": self.test_id
        }
        json = self.config['test_93_export']['payload']
        response = self.app.post('/api/v1/table/action',
                                 headers=headers, json=json)
        # pattern = re.compile(r'^{"file_path": '
        #                      r'".*days-kernel(\\|\/)exports(\\|\/)'
        #                      r'9a5f0cb0-5443-4aa4-bc10-8bf0d4e15cd9\.csv"}$')
        # self.assertTrue(bool(pattern.match(response.data.decode("utf-8"))))
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()