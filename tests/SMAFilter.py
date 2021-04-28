import matplotlib.pyplot as plt
outFile = open("SMAoutput.txt", "w")
#initialize variables
x = []
y=[]
line = 0
averages = []
numInSMA = 3


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


def simpleMovingAve(time, data, numInAve):
    sumArray = []
    for i in range(numInAve - 1):
        averages.append(data[0])

    for i in range(numInAve - 1, len(time)):
        counter = numInAve - 1
        while counter >= 0:
            sumArray.append(data[i - counter])
            counter = counter - 1

        averages.append(sum(sumArray) / numInAve)
        sumArray.clear()


x = timeoutput("data.log")

row = 1
allValues = [[], [], [], [], [], [], [], []]
tempValues = []
for i in range(0, len(x)):
    allValues[0].append(x[i])

#loops for all of the data sets
for j in range(1, 8):
    y = listoutput("data.log", j)
    simpleMovingAve(x, y, numInSMA)


    for values in range(len(averages)):
        allValues[row].append(averages[values])

    row = row + 1


    y.clear()
    averages.clear()


#output to file using proper formatting
outFile.write("time (s),gx (dps),gy (dps),gz (dps),ax (g),ay (g),az (g),temp (C)\n")
for values in range(len(allValues[0])):
    outFile.write(str(allValues[0][values]) + ", " + str(allValues[1][values]) + ", " + str(allValues[2][values]) +
                  ", " + str(allValues[3][values]) + ", " + str(allValues[4][values]) + ", " + str(allValues[5][values])
                  + ", " + str(allValues[6][values]) + ", " + str(allValues[7][values]) + "\n")

outFile.close()
allValues.clear()


SMAx = listoutput("SMAoutput.txt", 0)

#create plots for each data set
for j in range(1, 8):
    SMAy = listoutput("SMAoutput.txt", j)
    y = listoutput("data.log", j)

    plt.figure(j)

    plt.plot(x, y, "g+", label = "Measured")
    plt.plot(SMAx, SMAy, label='SMA')

    plt.title(label = "SMA Figure " + str(j))
    plt.legend()
    plt.savefig("SMA"+str(j)+".jpg")

    y.clear()
    SMAy.clear()

