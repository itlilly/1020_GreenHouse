from engi1020.arduino.api import*

def get_temp():
    return temp_humid_get_temp(3)


def get_humid():
    return temp_humid_get_humidity(3)


def get_moist():
    return round(analog_read(0)/950*100, 1)


def heating_status(desired, actual):
    if desired > actual:
        if digital_read(2) is False:
            digital_write(2, True)
        return True
    else:
        if digital_read(2) is True:
            digital_write(2, False)
        return False


def valve_status(desired, actual):
    if desired > actual:
        if servo_get_angle(6) == 0:
            servo_set_angle(6, 90)
        return True
    else:
        if servo_get_angle(6) == 90:
            servo_set_angle(6, 0)
        return False


def control_default():
    digital_write(2, False)
    servo_set_angle(6, 0)
    return '''Heating: OFF
Valve: OFF'''


def data_stats(data):
    data_types = data.keys()
    for key in data_types:
        if data[key][0] > data[key][-1]:
            delta = "decreased"
        elif data[key][0] < data[key][-1]:
            delta = "increased"
        else:
            delta = "none"

        if key != "time":
            print(f"Average {key}: {round(sum(data[key])/len(data[key]), 2)}")
            if delta != 'none':
                print(
                  f"{key.capatalize()} has {delta} " +
                      f"by {round(data[key][-1] - data[key][0], 2)}"
                )
            else:
                print(f"{key.capatalize()} has not changed")
