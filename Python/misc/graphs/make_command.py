#!/usr/bin/python

g={ "config":    ["app","system","firewall"],
    "app":       ["tim","dsrcproxy","ipv6","gpsoutput"],
    "tim":       ["ifname","streaming"],
    "ifname":    ["ath0","ath1"],
    "streaming": ["mode","ip","port"],
    "dsrcproxy": [],
    "firewall":  [],
    "ath0":      [],
    "ath1":      [],
    "mode":      [],
    "ip":        [],
    "port":      [],
    "ipv6":      [],
    "gpsoutput": [],
    "system":    []
}
def find_path(graph, start, end, path=[]):
        path = path + [start]
        if start == end:
            return path
        if not graph.has_key(start):
            return None
        for node in graph[start]:
            if node not in path:
                newpath = find_path(graph, node, end, path)
                if newpath: return newpath
        return None
fin=""
commands=[]
cm=find_path(g,"config","ath1")
for x in cm:
	fin=fin+" "+x
commands.append(fin.strip())

print commands
