import matplotlib.pyplot as plt
outFile = open("EMAoutput.txt", "w")

#initialize variables
x = []
y = []
line = 0

EMAMultiplier = .1
EMA = []

#Dev's code for importing data from the files
def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1
def listoutput(fname, lineNum):
    myFile = open(fname)
    lines = file_len(fname)
    #print(lines)
    data = myFile.readline()
    temps = []
    for i in range(lines-2):
        data = myFile.readline().split(',')
        temp = data[lineNum]
        temp = temp.strip('\n')
        temp = float(temp)
        temps.append(temp)
    return temps
def timeoutput(fname):
    myFile = open(fname)
    lines = file_len(fname)
    data = myFile.readline()
    times = []
    for i in range(lines-2):
        data = myFile.readline().split(',')
        time = data[0]
        time = float(time)
        times.append(time)
    return times

#exponential moving average filter
def exponentialMovingAve(time, data, multiplier):
    EMA.append(data[0])

    for i in range(1, len(time)):
        newEMA = data[i] * multiplier + EMA[i-1] * (1 - multiplier)
        EMA.append(newEMA)



x = timeoutput("data.log")

row = 1
allValues = [[], [], [], [], [], [], [], []]
tempValues = []

#set first array in the multidimensional array to time
for i in range(0, len(x)):
    allValues[0].append(x[i])

#loops for all of the data sets
for j in range(1, 8):
    y = listoutput("data.log", j)
    exponentialMovingAve(x, y, EMAMultiplier)


    for values in range(len(EMA)):
        allValues[row].append(EMA[values])

    row = row + 1

    y.clear()

    EMA.clear()

#output to file using proper formatting
outFile.write("time (s),gx (dps),gy (dps),gz (dps),ax (g),ay (g),az (g),temp (C)\n")
for values in range(len(allValues[0])):
    outFile.write(str(allValues[0][values]) + ", " + str(allValues[1][values]) + ", " + str(allValues[2][values]) +
                  ", " + str(allValues[3][values]) + ", " + str(allValues[4][values]) + ", " + str(allValues[5][values])
                  + ", " + str(allValues[6][values]) + ", " + str(allValues[7][values]) + "\n")

outFile.close()
allValues.clear()



EMAx = listoutput("EMAoutput.txt", 0)

#plots for each data set
for j in range(1, 8):
    EMAy = listoutput("EMAoutput.txt", j)
    y = listoutput("data.log", j)

    plt.figure(j)

    plt.plot(x, y, "g+", label = "Measured")
    plt.plot(EMAx, EMAy, label='EMA')

    plt.title(label = "EMA Figure " + str(j))
    plt.legend()
   ## plt.show()
    plt.savefig("EMA"+str(j)+".jpg")

    y.clear()
    EMAy.clear()

