from engi1020.arduino.api import *
import multiprocessing
import time


#Finds the change in value of a specific sensor over an inputed period of time
def delta_info(data, time):
#Takes inputed to and creates closest 10 second increment
    time_period = int(time/10)
#Checks if time request is within time range of list
    if time_period >= len(data):
#If out of range time and the 10 second increment set to oldest value
        list_index = 0
        time = 300
    else:
#If in range the index will be set to access corosponding value
        list_index = -1-time_period
#Finds the change in the data over the specific period of time
    delta = data[list_index] - data[-1]
#Returns a string corosponding the value of delta, and the sensor the data came from
    if delta > 0:
        if data == list_temp:
            return f'Temperature has increased by {delta} degrees over {time} seconds'
        elif data == list_humid:
            return f'Humidity has increased by {delta} over {time} seconds'
        elif data == list_moist:
            return f'Moisture content has increased by {delta} over {time} seconds'
    elif delta < 0:
        if data == list_temp:
            return f'Temperature has decreased by {delta} degrees over {time} seconds'
        elif data == list_humid:
            return f'Humidity has decreased by {delta} over {time} seconds'
        elif data == list_moist:
            return f'Moisture content has decreased by {delta} over {time} seconds'
    elif delta == 0:
        if data == list_temp:
            return f'Temperature has not changed over {time} seconds'
        elif data == list_humid:
            return f'Humidity has not changed over {time} seconds'
        elif data == list_moist:
            return f'Moisture content has not changed over {time} seconds'
    else:
        return 'An error has occured'
    


#Creates a list of values from each sensor in 10 second intervals
def list_info(v_temp, list_temp, v_humid, list_humid, v_moist, list_moist):
    while True:
        #Identical for each sensor
        with v_temp.get_lock():
            #Cretes new data value from sensor to be added to the list
            v_temp.value = temp_humid_get_temp(3)
            #Will remove oldest data value if the list is already at max lenght (30)
            if len(list_temp) == 30:
                list_temp.remove(0)
            #Will add new data value to the end of the list
            list_temp.append(v_temp.value)
        with v_humid.get_lock():
            v_humid.value = temp_humid_get_humidity(3)
            if len(list_humid) == 30:
                list_humid.remove(0)
            list_humid.append(v_humid.value)
        with v_moist.get_lock():
            v_moist.value = analog_read(n)
            if len(list_moist) == 30:
                list_moist.remove(0)
            list_moist.append(v_moist.value)
        time.sleep(10)
        

#Get instananeous data for each sensor
def instant_info(inst_temp, inst_humid, inst_moist):
    while True:
        #Identical for each sensor
        with inst_temp.get_lock():
            #Gets value of sensor
            inst_temp.value = temp_humid_get_temp(3)
        with inst_humid.get_lock():
            inst_humid.value = temp_humid_get_humidity(3)
        with inst_moist.get_lock():
            inst_moist.value = analog_read(n)
        time.sleep(1)
    

     
if __name__ == "__main__":
    
    #Defines the start value of each variable used by multiple processes
    inst_temp.Value = multiprocessing.Value('f', temp_humid_get_temp(3))
    inst_humid.Value = multiprocessing.Value('f', temp_humid_get_humidity(3))
    inst_moist.Value = multiprocessing.Value('f', analog_read(n))
    v_temp.Value = multiprocessing.Value('f', temp_humid_get_temp(3))
    v_humid.Value = multiprocessing.Value('f', temp_humid_get_humidity(3))
    v_moist.Value = multiprocessing.Value('f', analog_read(n))
    
    
    inst_temp.Value('f', temp_humid_get_temp(3))
    inst_humid.Value('f', temp_humid_get_humidity(3))
    inst_moist.Value('f', analog_read(n))
    v_temp.Value('f', temp_humid_get_temp(3))
    v_humid.Value('f', temp_humid_get_humidity(3))
    v_moist.Value('f', analog_read(n))
    
    #Defines the lists used by multiple processes
    with multiprocessing.Manager() as manager:
        list_temp = manager.list()
        list_humid = manager.list()
        list_moist = manager.list()
        
        #Defines two indenpendant processes, one for list info and the other for instantaneous info
        process_list_info = multiprocessing.Process(target=list_info, args=(v_temp, list_temp, v_humid, list_humid, v_moist, list_moist))
        process_instant_info = multiprocessing.Process(target=instant_info, args=(inst_temp, inst_humid, inst_moist))
        
        #Starts each defined process
        process_list_info.start()
        process_instant_info.start()
        
        while True:
            if input('check temp?: ') == 'yes':
                print(inst_temp, list_temp)
            if input('check humidity?') == 'yes':
                print(inst_humid, list_humid)
            if input('check moisture?') == 'yes':
                print(inst_moist, list_moist)
                
            
        
        