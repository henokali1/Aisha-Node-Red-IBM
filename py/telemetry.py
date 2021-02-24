from djitellopy import tello

me = tello.Tello()

me.connect()
telemetry=[]

telemetry.append(f'get_speed(): {me.get_speed()}')
telemetry.append(f'get_battery(): {me.get_battery()}')
telemetry.append(f'get_flight_time(): {me.get_flight_time()}')
telemetry.append(f'get_height(): {me.get_height()}')
telemetry.append(f'get_attitude(): {me.get_attitude()}')
telemetry.append(f'get_barometer(): {me.get_barometer()}')
telemetry.append(f'get_distance_tof(): {me.get_distance_tof()}')

for i in telemetry:
    print(i)
