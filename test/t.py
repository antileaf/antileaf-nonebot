from pack import foo, goo

print(goo())

import os

os.system('cd tt & mkdir ttt')
os.system('mkdir ttt')
os.system('cd ..')

f = open('tt/ttt/tt.txt', 'wt')

print('test', file = f)

f.close()

for s in os.listdir('tt'):
    print(s)
    if os.path.isdir('tt/' + s):
        print('is dir')