# DAYS-KERNEL

DAYS back-end kernel python-pandas codebase for file handling.

## Serving Flask app "app.app"

Run in shell window (5000 would be the port):
```shell
python3 run.py 5000
```

## API Request List
### -- POST --
#### UPLOAD FILE
```shell
curl --request POST \
  --url http://localhost:5000/api/v1/upload-file \
  --header 'Content-Type: multipart/form-data' \
  --header 'content-type: multipart/form-data; boundary=---011000010111000001101001' \
  --header 'id: {unique id}' \
  --header 'name: {name}' \
  --header 'size: 105338' \
  --form file=@{local_file_path}
```
Will load file into data frame and assign it to a global variable for later use.

#### READ FILE CONTENT
```shell
curl --request POST \
  --url http://localhost:5000/api/v1/read-file-contents \
  --header 'id: {unique id}' \
  --header 'name: {name}' \
  --header 'size: {size}' \
  --data '{file contents}'
```
Will load file into data frame and assign it to a global variable for later use.

#### GET TABLE DATA
```shell
curl --request GET \
  --url http://localhost:5000/api/v1/table/data \
  --header 'Content-Type: application/json' \
  --header 'id: {unique id}' \
  --data '{
	"startIndex": {start index},
	"rowCount": {row count}
}'
```
Will return the data starting at startIndex until rowCount.

##### return
```json
{
    "first_name": {
        "0": "Nydia",
        "1": "Jo",
        "2": "Arron",
        "3": "Sibylle",
        "4": "Shaun"
    },
    "last_name": {
        "0": "Hecks",
        "1": "Havock",
        "2": "Marrington",
        "3": "Mathiot",
        "4": "Gregh"
    },
    "email": {
        "0": "nhecks0@cnet.com",
        "1": "jhavock1@tripadvisor.com",
        "2": "amarrington2@ycombinator.com",
        "3": "smathiot3@gov.uk",
        "4": "sgregh4@friendfeed.com"
    },
    "gender": {
        "0": "Female",
        "1": "Male",
        "2": "Male",
        "3": "Female",
        "4": "Female"
    },
    "phone_number": {
        "0": "216-409-9183",
        "1": "502-451-4133",
        "2": "281-500-2488",
        "3": "850-935-9073",
        "4": "303-983-8936"
    },
    "dob": {
        "0": "1/29/2003",
        "1": "4/20/2014",
        "2": "8/4/1994",
        "3": "3/27/2011",
        "4": "7/29/1943"
    },
    "address": {
        "0": "69 Harbort Park",
        "1": "06 Victoria Pass",
        "2": "2 Eagle Crest Center",
        "3": "01312 Spohn Way",
        "4": "634 Comanche Park"
    },
    "city": {
        "0": "Cleveland",
        "1": "Louisville",
        "2": "Pasadena",
        "3": "Panama City",
        "4": "Denver"
    },
    "state": {
        "0": "Ohio",
        "1": "Kentucky",
        "2": "Texas",
        "3": "Florida",
        "4": "Colorado"
    },
    "cc_number": {
        "0": "378282246310005",
        "1": "371449635398431",
        "2": "378734493671000",
        "3": NaN,
        "4": "30569309025904"
    }
}
```

### -- GET --
#### GET TABLE INFO
```shell
curl --request GET \
  --url http://localhost:5000/api/v1/table/info \
  --header 'id: {unique id}'
```
Will return the schema of working file.

##### return
```json
{
  "ColumnCount": 10,
  "Columns": [
    {
      "customType": "",
      "dataType": "object",
      "displayName": "first_name",
      "distinctCount": 942,
      "extended": {},
      "index": 0,
      "name": "first_name",
      "nonNullCount": 1000,
      "visible": true
    },
    {
      "customType": "",
      "dataType": "object",
      "displayName": "last_name",
      "distinctCount": 980,
      "extended": {},
      "index": 1,
      "name": "last_name",
      "nonNullCount": 1000,
      "visible": true
    },
    {
      "customType": "",
      "dataType": "object",
      "displayName": "email",
      "distinctCount": 1000,
      "extended": {},
      "index": 2,
      "name": "email",
      "nonNullCount": 1000,
      "visible": true
    },
    {
      "customType": "",
      "dataType": "object",
      "displayName": "gender",
      "distinctCount": 2,
      "extended": {},
      "index": 3,
      "name": "gender",
      "nonNullCount": 1000,
      "visible": true
    },
    {
      "customType": "",
      "dataType": "object",
      "displayName": "phone_number",
      "distinctCount": 1000,
      "extended": {},
      "index": 4,
      "name": "phone_number",
      "nonNullCount": 1000,
      "visible": true
    },
    {
      "customType": "",
      "dataType": "object",
      "displayName": "dob",
      "distinctCount": 986,
      "extended": {},
      "index": 5,
      "name": "dob",
      "nonNullCount": 1000,
      "visible": true
    },
    {
      "customType": "",
      "dataType": "object",
      "displayName": "address",
      "distinctCount": 1000,
      "extended": {},
      "index": 6,
      "name": "address",
      "nonNullCount": 1000,
      "visible": true
    },
    {
      "customType": "",
      "dataType": "object",
      "displayName": "city",
      "distinctCount": 306,
      "extended": {},
      "index": 7,
      "name": "city",
      "nonNullCount": 1000,
      "visible": true
    },
    {
      "customType": "",
      "dataType": "object",
      "displayName": "state",
      "distinctCount": 50,
      "extended": {},
      "index": 8,
      "name": "state",
      "nonNullCount": 1000,
      "visible": true
    },
    {
      "customType": "",
      "dataType": "object",
      "displayName": "cc_number",
      "distinctCount": 41,
      "extended": {},
      "index": 9,
      "name": "cc_number",
      "nonNullCount": 1000,
      "visible": true
    }
  ],
  "RowCount": 1000,
  "SizeInKb": "105338",
  "TableName": "mock_data.csv"
}
```

#### CLEAR WORKING FILE
```shell
curl --request GET \
  --url http://localhost:5000/api/v1/clear-workingfile \
  --header 'id: {unique id}'
```
Will delete the working file from memory.

### -- PUT --
#### PUT TABLE ACTION
```shell
curl --request PUT \
  --url http://localhost:5000/api/v1/table/action \
  --header 'Content-Type: application/json' \
  --header 'id: {unique id}' \
  --data '{
	"action": "{action type}",
	"inputParams": [
		{
			{input params}
		}
	]
}'
```
Will edit working file and update corresponding schema.

#### PUT TABLE INFO
```shell
curl --request PUT \
  --url http://localhost:5000/api/v1/table/info \
  --header 'Content-Type: application/json' \
  --header 'id: {unique id}' \
  --data '{
	"tableSchema": [
		{
			"index": 10,
			"visible": false
    }
	]
}'
```
Will edit schema given updates in json.


## Packages
### Controllers

app/controllers/objects.py
```
    ActiveWorkingFiles:
        class serves as global variable in app contains list of WorkingFile objects

    WorkingFile:
        class inputs DataFrame object and creates a schema object referencing the DataFrame

    Schema:
        class creates schema dictionary based on DataFrame object

    Columns:
        class handles changing indexes and reconciles schema of new DataFrame
```

### Handler

app/handler/base.py
```
    Handler:
        class inputs table action and executes on DataFrame
```

app/handler/validator.py
```
    Validator:
        class that handles validation table actions
```

### Ingester

app/ingester/base.py
```
    Ingester:
        class inputs file parameters and outputs a DataFrame
```

### Profiler

app/profiler/base.py
```
    Profiler:
        class inputs DataFrame and returns profile statistics
```

### Resources

app/resources/base.py
```
    GenericCall:
        class handles generic flask request object

    UploadFile(GenericCall):
        class inputs request object for 'upload-file' call

    ReadFileContents(GenericCall):
        class inputs request object for 'read-file-contents' call

    TableSchema(GenericCall):
        class inputs request object for 'table-schema' call

    ClearWorkingTable(GenericCall):
        class inputs request object for 'clear-working-table' call

    TableData(GenericCall):
        class inputs request object for 'table-data' call

    TableAction(GenericCall):
        class inputs request object for 'table-action' call
```