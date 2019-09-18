import sys, os
sys.path.append(os.path.abspath(os.path.join('..', 'logs')))

if __name__ == '__main__':
    log = open('../logs/test.log', 'a+')
    log.write('test1,test2,test3\n')
    x = 1
    y = 2
    z = 3
    log.write(f'{x},{y},{z}\n')
    log.close()
