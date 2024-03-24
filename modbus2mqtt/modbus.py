import config
from pyModbusTCP.client import ModbusClient

class modbus_getwate:
    def __init__(self, Host,Name,key,Port=502,):
        self.__Host = Host 
        self.__Port = Port
        self.__Name= Name
        self.__key=key
        self.__ecl=ModbusClient(host=self.__Host, port=self.__Port, auto_open=True,debug=False)
        self.__read_val={}

    def __read(self,reg_addr,reg_type,b32=False):
        if b32==False:pin=1
        else: pin=2
        #01 Чтение DI	Read Input Status	Дискретное	Чтение
        #02 Чтение DO	Read Coil Status	Дискретное або		
        #03 Чтение AO	Read Holding Registers	16 битное	
        #04 Чтение AI	Read Input Registers	16 битное	
        #0 - Чтение двох регістрів починаючи з адреси меншої 10 буде прочитано (10-11) де 10-стар 11-мол 
        if reg_type==1:
            return self.__ecl.read_discrete_inputs(reg_addr-1,pin)
        if reg_type==2:
            return self.__ecl.read_coils(reg_addr-1,pin)
        if reg_type==3:
            return self.__ecl.read_input_registers(reg_addr-1,pin)    
        if reg_type==4:
            return self.__ecl.read_holding_registers(reg_addr-1,pin)

    def __pld(self,reg_addr,reg_type,pld_type=0,pld_param=0):
         # pld_type 0 - ціле1 – з десятими 2– з сотими 3– з тисячними 4 – бітова маска 5 – 32 бітне значення
        if 0 <= pld_type <= 3:
             val=self.__read(reg_addr,reg_type)
             if val==None: return None
             Kr=10**pld_type
             return val[0]/Kr
        #4 – бітова маска
        elif pld_type==4:
             val=self.__read(reg_addr,reg_type)
             if val==None: return None
             mask = 1 << pld_param
             # Перевіряємо, чи встановлений біт на вказаній позиції у числі
             if val[0] & mask:return 1  # Біт встановлено
             else: return 0  # Біт не встановлено
        elif pld_type==5: 
            val=self.__read(reg_addr,reg_type,True)
            if val==None: return None
            if pld_param==0:
                val=(val[0] << 16) | val[1]
            elif pld_param==1:
                val=(val[1] << 16) | val[0]
            return val
    
    def __val_diff(self,reg_addr,reg_type,pld_type=0,pld_param=0,diff=0):
        val=self.__pld(reg_addr,reg_type,pld_type,pld_param)
        #print("i tyt")
        if val==None: return None
        if reg_type in self.__read_val and reg_addr in self.__read_val[reg_type]:
            if (val + diff) < self.__read_val[reg_type][reg_addr] or self.__read_val[reg_type][reg_addr] < (val + diff):
                self.__read_val[reg_type][reg_addr] = val
                return val
        else:
            self.__read_val[reg_type] = {}
            self.__read_val[reg_type][reg_addr] = val
            return val
    def read(self,reg_addr,reg_type,pld_type=0,pld_param=0,diff=0):
        return self.__val_diff(reg_addr,reg_type,pld_type,pld_param,diff)