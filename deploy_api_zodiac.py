from requests import get, put, post
from plastering.metadata_interface import *
from plastering.uis import *

url = 'http://127.0.0.1:5000/'

def deploy():
    while True:
        params = {}
        response = get(url, params).json()
        print(response)
        expert_label = input('Enter point_tagset: ')
        data = {'srcid': response['srcid'], 'building': response['building'], 'expert_label': expert_label}
        post(url, data)

def recover_data():
    data = {'srcid': '1846', 'building': 'ghc', 'expert_label':'heating_request_setpoint'}
    post(url, data)

def main():
    deploy()
    # recover_data()

if __name__ == "__main__":
    main()

