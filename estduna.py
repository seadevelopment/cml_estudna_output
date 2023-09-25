#!/usr/bin/env python
"""
CML - How to get value of water level for you eStudna device

2022-05-17 v1-01
a) Project foundation
"""
import requests
import json
from time import sleep

# ----------------------------------------------------------------------------
# --- Configuration
# ----------------------------------------------------------------------------

# --- Configuration
username = 'zakznik@gmail.com'
password = 'heslo'
sn = 'SB817112'   # Serial number of your eSTUDNA


# ----------------------------------------------------------------------------
# --- Code
# ----------------------------------------------------------------------------

def httpPost(url, header={}, params={}, data={}):
    headers = {
      "Content-Type": "application/json",
      "Accept": "application/json",
      **header
    }
    data=json.dumps(data)
    r = requests.post(url=url, data=data, headers=headers, params=params)
    r.raise_for_status()

    return r.json()


def httpGet(url, header={}, params={}):

    headers = {
      "Content-Type": "application/json",
      "Accept": "application/json",
      **header
    }
    r = requests.get(url=url, headers=headers, params=params) 
    r.raise_for_status()

    return r.json()


class ThingsBoard:
    """
    Objekt pro pristup k Thingsboardu
    """


    def __init__(self):
        self.server = 'https://cml.seapraha.cz'
        self.userToken = None
        self.customerId = None
   

    def login(self, username: str, password: str):
        """
        Prihlaseni uzivatele
        """
        # Login
        url = f'{self.server}/api/auth/login'
        response = httpPost(url, {}, data={'username': username, 'password': password})
        self.userToken = response["token"]  # User token

        # Get customer ID
        url = f'{self.server}/api/auth/user'
        response = httpGet(url, {'X-Authorization': f"Bearer {self.userToken}"})
        self.customerId = response["customerId"]["id"]  # Customer ID


    def getDevicesByName(self, name: str):
        """
        Vyhledani zarizeni podle nazvu
        """
        url = f'{self.server}/api/customer/{self.customerId}/devices'
        params = {'pageSize': 100, 'page': 0, "textSearch": name}
        response = httpGet(url, {'X-Authorization': f"Bearer {self.userToken}"}, params=params)
        if (response["totalElements"] < 1):
            raise Exception(f"Device SN {name} has not been found!")

        return response["data"]


    def getDeviceValues(self, deviceId, keys):
        """
        Cteni aktualnich hodnot ze zarizeni
        """
        url = f'{self.server}/api/plugins/telemetry/DEVICE/{deviceId}/values/timeseries'
        params = {'keys': keys}
        response = httpGet(url, {'X-Authorization': f"Bearer {self.userToken}"}, params=params)

        return response
    

    def setDeviceOutput(self, deviceId, output: str, value: bool):

        output = "setDout1" if output == "OUT1" else "setDout2"

        data = {"method": output, "params": value}
        url = f'{self.server}/api/rpc/twoway/{deviceId}'
        response = httpPost(url, {'X-Authorization': f"Bearer {self.userToken}"}, params={}, data=data)

        return response


def eStudna_GetWaterLevel(username: str, password: str, serialNumber: str) -> float:
    """
    Cteni hladiny ve studni
    """
    tb = ThingsBoard()
    tb.login(username, password)
    user_devices = tb.getDevicesByName(f"%{serialNumber}")
    values = tb.getDeviceValues(user_devices[0]["id"]["id"], "ain1")
    return values["ain1"][0]["value"]


def eStudna_SetOutput(username: str, password: str, serialNumber: str, output: str, state: bool):
    tb = ThingsBoard()
    tb.login(username, password)
    user_devices = tb.getDevicesByName(f"%{serialNumber}")
    tb.setDeviceOutput(user_devices[0]["id"]["id"], output, state)




# ----------------------------------------------------------------------------
# --- Main code
# ----------------------------------------------------------------------------

level = eStudna_GetWaterLevel(username, password, sn)
print(f"Device: {sn}")
print(f"Water level: {level}")

eStudna_SetOutput(username, password, sn, "OUT1", True)
print(f"OUT1: true")
sleep(1.0)
eStudna_SetOutput(username, password, sn, "OUT1", False)
print(f"OUT1: false")

# End of file
