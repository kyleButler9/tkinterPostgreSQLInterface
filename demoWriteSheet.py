from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from config import config
# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def createSheet(title):
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    spreadsheet = {
        'properties': {
            'title': title
        }
    }
    spreadsheet = service.spreadsheets().create(body=spreadsheet,
                                        fields='spreadsheetId').execute()
    #print('Spreadsheet ID: {0}'.format(spreadsheet.get('spreadsheetId')))
    return spreadsheet.get('spreadsheetId')
def parseSheetsHTTP(http):
    if len(http) > 50:
        bc = r'/d/'
        ec = r'/edit'
        begin = http.index(bc) + len(bc)
        end = http.index(ec)
        return http[begin:end]
    else:
        return http
def write_to_sheet(spreadsheet_id, values):
    """Shows basic usage of the Sheets API.
    overwrites values in a given spreadsheet.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    #values = [[1,2,3],['a','b','c']]
    #spreadsheet_id='1bYtdVyFiVKj_2bRLk2pLKoXGF851r8_cSrbFvYgOZ6c'
    body = {
        'values': values
    }
    range_name='Sheet1!A1:I10000'
    value_input_option = 'USER_ENTERED'
    result = service.spreadsheets().values().update(
        spreadsheetId=parseSheetsHTTP(spreadsheet_id), range=range_name,
        valueInputOption=value_input_option, body=body).execute()
    out='{0} cells updated.'.format(result.get('updatedCells'))
    return out
def append_to_sheet(spreadsheet_id, values):
    """Shows basic usage of the Sheets API.
    appends values to a given spreadsheet.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    #values = [[1,2,3],['a','b','c']]
    #spreadsheet_id='1bYtdVyFiVKj_2bRLk2pLKoXGF851r8_cSrbFvYgOZ6c'
    body = {
        'values': values
    }
    range_name='Sheet1!A1:I10000'
    value_input_option = 'USER_ENTERED'
    insert_Data_Option = 'INSERT_ROWS'
    result = service.spreadsheets().values().append(
        spreadsheetId=parseSheetsHTTP(spreadsheet_id), range=range_name,
        valueInputOption=value_input_option,insertDataOption=insert_Data_Option, body=body).execute()
    out='{0} cells updated.'.format(result.get('updatedCells'))
    return out
if __name__ == '__main__':
    #createSheet('demo creation')
