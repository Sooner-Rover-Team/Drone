#this code enables the RaspberryPi to connect to the quad-copter

from dronekit import connect

#connect to drone and this will also download
#all of the quadciopter attributes under the object vehicle
vehicle = connect('/dev/serial0',baud=57600, wait_ready=True)

# Get some vehicle attributes (state)
print "Get some vehicle attribute values:"
print " GPS: %s" % vehicle.gps_0
print " Battery: %s" % vehicle.battery
print " Last Heartbeat: %s" % vehicle.last_heartbeat
print " Is Armable?: %s" % vehicle.is_armable
print " System status: %s" % vehicle.system_status.state
print " Mode: %s" % vehicle.mode.name    # settable
