import sys
import os

#print("Argument List:", str(sys.argv)) #prints list of arguments, sys.argv[0] is the name of the file, the rest are those that follow

fileName = sys.argv[1] #name of the file being passed in
unrollNum = int(sys.argv[2])# number of times needed to unroll
targetState = str(sys.argv[3]) #target state as a string of 0 and 1s

verFile = open(fileName, 'r') # open the file in read mode
dimacsFile = open("dimacsFile.dimacs","w") #create a dimacs file and open in write mode

dimacsDict = {}


dimacsNum = 1
currentUnroll = 0
dictDone = 0
statementNum = 0

while currentUnroll < unrollNum:
    while True:

        line = verFile.readline().split() #splits up each line and returns a list of each word, This will seperate the gate name from the gate inputs
        if not line:
            currentUnroll = currentUnroll + 1
            verFile.seek(0) #start over at beginning
            break
        # if count >=3 and count <=6 and currentUnroll ==0 and dictDone==0: #find all of the variables from the verilog file
        #     valuesComb = line[1] #gives inputs, outputs, etc
        #     splitVal = valuesComb.split(',')
        #     cleanVal = [vals.replace(';', '') for vals in splitVal]
        #     for i in cleanVal:
        #         dimacsDict[i] = dimacsNum #adds verilog variables to a dictionary with a incremented key value
        #         dimacsNum = dimacsNum + 1
        #     print(dimacsDict)
        #     #continue # keep so it goes back to the top of the while loop and doesnt continue into the else statement later
        gateType = line[0]
        if (gateType=="input" or gateType=="output" or gateType=="wire" or gateType=="reg") and dictDone==0: # going to be placing all of the variables into the dict, only need to do on first pass through
            valuesComb = line[1]
            splitVal = valuesComb.split(',')
            cleanVal = [vals.replace(';','') for vals in splitVal]
            for i in cleanVal:
                dimacsDict[i] = dimacsNum
                dimacsNum = dimacsNum+1
            if line[0]=="wire" and len(line)!=3: #wire is always the last of the declarations, once this is done, all values will be in the dict
                dictDone=1
                print(dimacsDict)
            continue
        #print(gateType)
        if gateType == "and":
            gateVals = line[1].split(',')
            finGateVal = [vals.replace(");", "") for vals in gateVals]
            finGateVal[0] = finGateVal[0].split('(')[1] # takes off leading g...( leaving just the output gate

            # these give the corresponding numbers for each of the verilog input and outputs from the dictionary
            outputNum = str(dimacsDict[finGateVal[0]]+(len(dimacsDict)*currentUnroll))
            inputNum1 = str(dimacsDict[finGateVal[1]]+(len(dimacsDict)*currentUnroll))
            inputNum2 = str(dimacsDict[finGateVal[2]]+(len(dimacsDict)*currentUnroll))
            print("%s -%s 0\n%s -%s 0\n-%s -%s %s 0" %(inputNum1, outputNum, inputNum2, outputNum, inputNum1, inputNum2, outputNum))
            dimacsFile.write("%s -%s 0\n%s -%s 0\n-%s -%s %s 0\n" % (inputNum1, outputNum, inputNum2, outputNum, inputNum1, inputNum2, outputNum))
            statementNum+=3
            continue # used to not go into other loops
            # print(finGateVal) #0 is output, 1 and 2 are inputs

        if gateType == "not":
            gateVals = line[1].split(',')
            finGateVal = [vals.replace(");","") for vals in gateVals]
            finGateVal[0] = finGateVal[0].split('(')[1] # take of leading g..(

            outputNum = str(dimacsDict[finGateVal[0]]+(len(dimacsDict)*currentUnroll))
            inputNum1 = str(dimacsDict[finGateVal[1]]+(len(dimacsDict)*currentUnroll))
            print("-%s -%s 0\n%s %s 0" % (inputNum1, outputNum, inputNum1, outputNum))
            dimacsFile.write("-%s -%s 0\n%s %s 0\n" % (inputNum1, outputNum, inputNum1, outputNum))
            statementNum += 2
            continue

        if gateType == "always" or gateType == "end" or gateType == "endmodule" or gateType=="module" or gateType=="input" or gateType=="output" or gateType=="wire" or gateType=="reg":
            continue

        #if gateType != "always" or gateType != "end" or gateType != "endmodule":  #buffer statements
        else:
            #if currentUnroll == 0:
            gateVals = gateType.split("<=")
            finGateVal = [vals.replace(";","") for vals in gateVals]

            outputNum = str(dimacsDict[finGateVal[0]]+(len(dimacsDict)*(currentUnroll+1)))
            inputNum1 = str(dimacsDict[finGateVal[1]]+(len(dimacsDict)*currentUnroll))

            dimacsFile.write("-%s %s 0\n%s -%s 0\n" %(inputNum1, outputNum, inputNum1, outputNum))
            print("-%s %s 0\n%s -%s 0" %(inputNum1, outputNum, inputNum1, outputNum))
            statementNum += 2



numStates = len(targetState) # gives the number of state bits
State = dimacsDict["S0"]
inc = 1
for i in range(numStates):#write the initial state bits to 0
    dimacsFile.write("-%s 0\n" %(State+i))
    statementNum += 1
    #print("-%s 0" % (State+i))
nextState = dimacsDict["NS0"]
for i in targetState:
    if i == "1":
        dimacsFile.write("%s 0\n"%(nextState +((unrollNum-1)*len(dimacsDict))+numStates-inc))
        print("%s 0"%(nextState +((unrollNum-1)*len(dimacsDict))+numStates-inc))
        inc+=1
        statementNum += 1
    if i == "0":
        dimacsFile.write("-%s 0\n"%(nextState +((unrollNum-1)*len(dimacsDict))+numStates-inc))
        print("-%s 0" % (nextState + ((unrollNum-1) * len(dimacsDict)) +numStates-inc))
        inc += 1
        statementNum += 1

# have to add p line to beginning so have to create a new file
dimacsFile.close()
dimacsFile = open("dimacsFile.dimacs","r")
finFile = open("finDimFile.dimacs","w") #now have to append to the file so the top doesnt get overwritten
finFile.write("p cnf %s %s\n" % (len(dimacsDict)*unrollNum, statementNum))
for line in dimacsFile:
    finFile.write(line)

dimacsFile.close()
finFile.close()
verFile.close()

os.system("minisat finDimFile.dimacs output.txt") # calls the minisat command



#NEED TO DO MINISAT COMMAND AND GET REACHABILITY FROM THAT