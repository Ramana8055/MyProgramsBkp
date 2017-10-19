main_list=["config","show","enable"]

#config params
config_list=["app","system","firewall"]
config_app=["tim","dsrcproxy","ipv6","gpsoutput"]

#config_tim
config_tim=["ifname","enable","disable","streaming","security certattach-rate","transmit","review","commit"]
config_tim_streaming=["mode","port","ip"]
config_tim_transmit=["power","data-rate"]

#config_dp
config_dp=["ifname","enable","disable","listenerport","streaming","tcdlisten","security certattach-rate","transmit","review","commit"]
config_dp_streaming=["mode","port","ip"]
config_dp_transmit=["power","data-rate"]

#config_gpsoutput
config_gpsoutput=["port","interval"]

#config_ipv6 -->subject to change
#config_ipv6=["ifname",

#show params
show_list=["app","system","network","firewall"]
show_app=["tim","dsrcproxy","ipv6","gpsoutput"]
#show_tim
show_tim=["ifname","status","streaming","security certattach-rate","transmit","all"]
show_tim_streaming=["mode","port","ip"]
show_tim_transmit=["power","data-rate"]

#others
interface=["ath0","ath1"]
