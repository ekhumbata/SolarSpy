try:
  import urequests as requests
except:
  import requests
  
import network
import gc

import machine
import utime

gc.collect()

#wifi credentials for the rpi pico w
ssid = 
password = 

# Your Account SID and Auth Token from twilio.com/console
account_sid = 
auth_token = 

#phone numbers must be formatted as +17801234567
recipient_num = 
#number from twilio
sender_num = 

"""
This functions sends an SMS to the requested device via twilio
some code adapted from: https://microcontrollerslab.com/send-sms-raspberry-pi-pico-w-twilio/
"""
def send_sms(recipient, sender,
             message, auth_token, account_sid):
      
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = "To={}&From={}&Body={}".format(recipient,sender,message)
    url = "https://api.twilio.com/2010-04-01/Accounts/{}/Messages.json".format(account_sid)
    
    print("Trying to send SMS with Twilio")
    
    response = requests.post(url,
                             data=data,
                             auth=(account_sid,auth_token),
                             headers=headers)
    
    if response.status_code == 201:
        print("SMS sent!")
    else:
        print("Error sending SMS: {}".format(response.text))
    
    response.close()

"""
This function connects and confirms the connection to the R-Pi pico w
"""
def connect_wifi(ssid, password):
  station = network.WLAN(network.STA_IF)
  station.active(True)
  station.connect(ssid, password)
  while station.isconnected() == False:
    pass
  print('Connection successful')
  print(station.ifconfig())

"""
This function collects the requested number of measurments from the solar panel
and gives back data such as average voltage and average UV index
"""
def collectMeasurments(numMeasurements):

  #connections:
  #Sensor-to-MCU
  #3.3V-to-3.3V
  #Vin-to-ADC_VREF
  #GND-to-AGND
  #EN-to-3.3V
  #OUT-to-ADC1

  #reset lst_voltages
  lst_voltages = []
  #create list to hold all uv values
  lst_uv = []

  uv_sensor_datain = machine.ADC(1)  #get analog data from the ML8511 UV Sensor

  conversion_factor = 3.3/65536      #to convert analog data to voltage

  print("Collecting voltages...")

  #loop to output voltage and UV index values
  for x in range(numMeasurements):
    uv_volt_reading = uv_sensor_datain.read_u16() * conversion_factor
    uv_index = interpolation(uv_volt_reading,0.99,2.8,0.0,15.0)
    lst_voltages.append(uv_volt_reading)
    lst_uv.append(uv_index);
    print('Voltage Output:', uv_volt_reading,'V',',','UV Index: ', uv_index)
    utime.sleep(0.25)

  print("Voltages collected!")

  #get the average uv
  avg_uv = sum(lst_uv) / len(lst_uv)

  return lst_voltages, avg_uv



"""
This is a helper function to gather interpolation data for the UV
"""
def interpolation(uv_volt_reading, volt_in_min, volt_in_max, uv_intensity_min, uv_intensity_max):
    return (uv_volt_reading - volt_in_min) * (uv_intensity_max - uv_intensity_min) / (volt_in_max - volt_in_min) + uv_intensity_min


connect_wifi(ssid, password)

voltages, uv = collectMeasurments(25)


s1 = f"Max Voltage: {max(voltages)}"
s2 = f"Min Voltage: {min(voltages)}"
s3 = f"Average Voltage: {sum(voltages) / len(voltages)}"
s4 = f"UV Index: {uv}"

print(s1)
print(s2)
print(s3)
print(s4)

message = s1 + "\n" + s2 + "\n" + s3 + "\n" + s4
send_sms(recipient_num, sender_num, message, auth_token, account_sid)
