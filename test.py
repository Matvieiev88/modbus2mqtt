from modbus import modbus_getwate
import config
e=modbus_getwate(config.Host,config.Name,config.key)
print(e.read(6014,3,5,0))
