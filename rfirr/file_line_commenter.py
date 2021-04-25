''' Script that comments or uncomments desired config file lines'''
boot_conf = '/boot/config.txt'

with open(boot_conf, 'r') as fp:
    data = fp.readlines()

disable_bluetooth = 'dtoverlay=disable-bt\n'
disable_wifi = 'dtoverlay=disable-wifi\n'
disabled_connections = (disable_bluetooth, disable_wifi)
enabled_connections = tuple((('#' + x) for x in disabled_connections))

en_dis = {'enabled': [], 'disabled': []} 
for i, l in enumerate(data):
    print(l)
    if l in disabled_connections:
        en_dis['enabled'].append(i)
    if l in enabled_connections:
        en_dis['disabled'].append(i)

for k,v in en_dis.items():
    for vv in v:
        if k == 'disabled':
            data[vv] = data[vv].replace('#','')
        if k == 'enabled':
            data[vv] = '#' + data[vv]
for l in data:
    print(l)

#with open('stats.txt', 'w') as fp:
#    fp.writelines( data )
