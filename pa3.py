'''
Author: Jacob Powell Vince
Class: COMP370
4/27/2018

Program takes in an input file with a regular expression, alphabet, and test input strings;
converts regular expression to DFA, then test input strings on DFA.
Program uses StateSet class to represent a state of NFA/DFA and
RegexToDFA class whose methods convert the regular expression to DFA and tests if the
input strings are in the language of the original regular expression
'''


import sys
import string
import re
from collections import defaultdict

#class to represent states as sets of states; initialized with dictionary(char:list) of
#sets of state transitions mapped to symbols
class StateSet:
    def __init__(self):
        self.acceptState = False
        self.used = False   #does any transition sequence from start state reach state
        self.stateSet = [] #the set of states from which state transitions
        self.transitions = defaultdict(list)

#class to represent regex to DFA converter;
#Methods (in order of usage):
# - __init__()
# - convert()
# - regexToNFA()
# - combineEndStates()
# - setStateSets()
# - combineEpsilonStates()
# - NFAtoDFA()
class RegexToDFA:

    #initialize Object with line, alphabet, testStrings, states, rejectState
    def __init__(self, alphabet, line, testStrings):
        self.line = line
        self.alphabet = alphabet
        self.testStrings = testStrings
        self.states = []
        self.rejectState = -1

    #run regexToNFA(), setStateSets(), combineEpsilonStates(), NFAtoDFA(), popUnusedStates()
    def convert(self):
        self.startState, acceptState, lastop = self.regexToNFA(self.line, self.createState())
        self.states[acceptState].acceptState = True

        self.setStateSets()
        self.combineEpsilonStates()

        self.NFAtoDFA(self.startState)
        self.popUnusedStates()

    #create new state, append to states, return index in states
    def createState(self):
        newState = StateSet()
        self.states.append(newState)
        return len(self.states) - 1

    def printStates(self):
        for state in self.states:
            print(state.stateSet, state.transitions, state.acceptState)

    #used to compare equivalency of states' transition lists and stateSets
    def listCompare(self, x, y):
        same = set(x) & set(y)
        if len(same) == len(x) and len(same) == len(y):
            return True
        else:
            return False

    #initialize stateSets to current index in states
    def setStateSets(self):
        for x in range(len(self.states)):
            self.states[x].stateSet.append(x) #set of states

    #combine the endStates for OR operations
    def combineEndStates(self, end1, end2):
        for i in range(len(self.states)):
            for symbol in self.alphabet:
                if symbol in self.states[i].transitions:
                    if end2 in self.states[i].transitions[symbol]:
                        if end1 not in self.states[i].transitions[symbol]:
                            self.states[i].transitions[symbol].append(end1)
                        self.states[i].transitions[symbol].remove(end2)
        self.states.pop(end2)
        return end1

    #remove unused states, rename states/transitions to new placement
    def popUnusedStates(self):
        i=0
        while i < len(self.states):
            if not self.states[i].used:
                self.states.pop(i)
            else:
                i += 1
        #rename states and transitions to new position of states in states[]
        for j in range(len(self.states)):
            for i in range(len(self.states)):
                for symbol in self.alphabet:
                    if self.listCompare(self.states[j].stateSet, self.states[i].transitions[symbol]):
                        self.states[i].transitions[symbol] = [j]

    #combine states with epsilon transitions with the transition states
    def combineEpsilonStates(self):
        for i in range(len(self.states)):
            if 'e' in self.states[i].transitions:
                if len(self.states[i].transitions['e']) > 0: #has epsilon transition
                    for transition in self.states[i].transitions['e']:
                        if self.states[transition].acceptState == True: #is acceptState if epsilon transitions to acceptState
                            self.states[i].acceptState = True
                        for symbol in self.alphabet:
                            if symbol in self.states[transition].transitions:
                                for trans2 in self.states[transition].transitions[symbol]:
                                    if (trans2 not in self.states[i].stateSet): #transition of epsilon transition state doesn't go back to original state
                                        if trans2 not in self.states[i].transitions[symbol]:
                                            self.states[i].transitions[symbol].append(trans2)
                                    else: #transition goes back to original state, create transition from original state to original state
                                        for x in range(len(self.states)):
                                            for letter in self.alphabet:
                                                if transition in self.states[x].transitions[letter]:
                                                    self.states[x].transitions[letter].remove(transition)
                                                    self.states[x].transitions[letter].append(i)
                                self.states[i].transitions[symbol].sort()
                self.states[i].transitions.pop('e')
            self.states[i].stateSet.sort()

    #function takes in a string representing a regex and a startState from which the NFA builds
    #function recursively:
    # - calls nextOp on line
    # - handles OR, STAR, CONCAT, STAR-CONCAT, or Symbol
    # - calls regexToNFA() for line1 and line2 from nextOp()
    # - returns start state, end state, last operation
    #recursive calls continue until the expression splits down to single symbols, then returns to each
    #preceeding operator handler until the entire original expression is parsed
    def regexToNFA(self, line, startState):
        code, line1, line2 = self.nextOp(line)

        if code == 0: # OR | operation

            # run nextOp() on sublines to predict nature of sub-expressions
            testCode1, testLine1, testLine2 = self.nextOp(line1)
            testCode2, testLine1, testLine2 = self.nextOp(line2)
            if testCode1 == -1 or testCode2 == -1: #invalid expression
                print("Invalid Regular Expression")
                exit(0)
            elif testCode1 == 1 and testCode2 == 1: # STAR | STAR
                newStart1 = self.createState()
                newStart2 = self.createState()
                self.states[startState].transitions['e'].append(newStart1)
                self.states[startState].transitions['e'].append(newStart2)
                start1, end1, op1 = self.regexToNFA(line1, newStart1)
                start2, end2, op2 = self.regexToNFA(line2, newStart2)
                ends = [end1, end2]
                ends.sort()
            elif testCode1 == 1: # STAR | line
                newStart = self.createState()
                self.states[startState].transitions['e'].append(newStart)
                start1, end1, op1 = self.regexToNFA(line1, newStart)
                start2, end2, op2 = self.regexToNFA(line2, startState)
                ends = [end1, end2]
            elif testCode2 == 1: # line | STAR
                newStart = self.createState()
                self.states[startState].transitions['e'].append(newStart)
                start1, end1, op1 = self.regexToNFA(line1, startState)
                start2, end2, op2 = self.regexToNFA(line2, newStart)
                ends = [end2, end1]
            else: # | of symbols or concat of lines
                start1, end1, op1 = self.regexToNFA(line1, startState)
                start2, end2, op2 = self.regexToNFA(line2, startState)
                ends = [end1, end2]
                ends.sort()
            #combine end1 & end2 states
            # if endState from sub expressions has an epsilon transition (i.e. * op back to another state), combine endStates w/ new state
            if (len(self.states[ends[0]].transitions['e']) > 0) or (len(self.states[ends[1]].transitions['e']) > 0):
                newEnd = self.createState()
                self.states[ends[0]].transitions['e'].append(newEnd)
                self.states[ends[1]].transitions['e'].append(newEnd)
                endState = newEnd
            else: # combine endStates, keeps the lowest index of the two
                endState = self.combineEndStates(ends[0], ends[1])
            return startState, endState, '|'


        elif code == 1: # STAR OP (aba)*  a*  (a|b)*  (ab(a|b)*)*

            startState, endState, op1 = self.regexToNFA(line1, startState)
            if op1 == line1: # a* b* 0*
                self.states[startState].transitions[op1].remove(endState)
                self.states[startState].transitions[op1].append(startState)
                self.states[startState].transitions['e'].append(endState)
            else: # (a|b)* (aaabbba)*
                self.states[startState].transitions['e'].append(endState)
                self.states[endState].transitions['e'].append(startState)
            return startState, endState, '*'


        elif code == 2: # STAR OP (line1) CONCAT w/ line2

            startState, end1, op1 = self.regexToNFA(line1, startState)
            if op1 == '|':
                if startState != end1: #(ab|bb)*ab
                    self.states[end1].transitions['e'].append(startState)
            elif op1 in alphabet: # a*b*
                self.states[startState].transitions[op1].append(startState)
            start2, end2, op2 = self.regexToNFA(line2, end1)
            return startState, end2, 'c'


        elif code == 3: # concat line1 & line2

            startState, end1, op1 = self.regexToNFA(line1, startState)
            end1, end2, op2 = self.regexToNFA(line2, end1)
            return startState, end2, 'c'

        elif code == 4: #single symbol

            endState = self.createState()
            self.states[startState].transitions[line].append(endState)
            return startState, endState, line

        elif code == -1: #invalid expression

            print("Invalid Regular Expression")
            exit(0)


    #function takes in a line or substring of line representing a regex,
    # check if next operator is:
    # - OR
    # - STAR
    # - STAR concatted w/ basic
    # - CONCAT of two basics
    # - line = (...) ---> rerun nextOp(line[1:-1])
    # - Symbol
    #and returns the corresponding code and substrings of line
    def nextOp(self, line):
        parenths = 0
        for i in range(len(line)):
            if line[i] is '(':
                parenths += 1
            elif line[i] is ')':
                parenths -= 1
            elif (parenths == 0) and (line[i] == '|'): #(a|b)|a  (ab)|(ab)*  aa|ab|a
                return 0, line[i+1:], line[:i] # 0 = OR
        if parenths != 0: #number of parentheses aren't equal, not a valid regular expression
            return -1, "", ""
        parenths = 0
        split = -1
        for i in range(len(line)): #find split of concatenation
            if line[i] == '(':
                parenths += 1
            if line[i] == ')':
                parenths -= 1
            if parenths == 0:
                if i < len(line) - 1: #line ==  a(a|b) or aabab or (abb)*aa(a|ab) or (a|b|c)ab or (...)(..)* or (...)* or a*b*
                    split = i
                    break
        if split != -1:
            if line[split+1] == '*': #line == (a|b)* or (a|b)*(aba)
                if split+1 == len(line)-1: #(a|b)* or a* or (aa)*
                    return 1, line[:-1], "" #star op on regex
                else: #(a|b)*(aba) or a*b* or
                    return 2, line[:split+2], line[split+2:] #star op on regex1, concat op on regex2
            else: #a(a|b) or aa or abaaba or (a|b)ab(a|b)*
                return 3, line[:split+1], line[split+1:] #concat op on regex1 & regex2
        elif len(line) > 1: # line = (....)
            return self.nextOp(line[1:-1]) #basic op on substring within ()
        elif len(line) == 1: # symbol a b 0 1
            return 4, line, ""
        else: # empty line not a valid regular expression
            return -1, "", ""


    #function takes in the startState, checks if state:
    # -has transitions to multiple states --> check for matching StateSet or create new StateSet
    # -has no transitions for symbols in the alphabet --> set to rejectState
    #then recursively calls convertStates() for all the states to which current state transitions
    def NFAtoDFA(self, state):
        for symbol in self.alphabet: #sort transition lists for comparisons
            self.states[state].transitions[symbol].sort()

        if not self.states[state].used: #state already converted?
            self.states[state].used = True #unused states are discarded later
            for symbol in self.alphabet[:-1]:
                if len(self.states[state].transitions[symbol]) > 1: #transition for symbol leads to set of states
                    stateSet = False
                    for transition in self.states:
                        if self.states[state].transitions[symbol] == transition.stateSet: #check if state already exists with set of states == transitions
                            stateSet = True
                    if not stateSet:   #if state doesn't exist, make new state s.t. new state transitions = union of transitions of states in set
                        newState = StateSet()
                        for transition in self.states[state].transitions[symbol]:
                            newState.stateSet.append(transition) #add transition to stateSet of new state
                            if self.states[transition].acceptState:
                                newState.acceptState = True
                            for letter in self.alphabet[:-1]:
                                if len(self.states[transition].transitions[letter]) > 0:
                                    for x in self.states[transition].transitions[letter]:
                                        if x not in newState.transitions[letter]:
                                            newState.transitions[letter].append(x) #add transitions for set of states
                                newState.transitions[letter].sort()
                        newState.stateSet.sort()
                        self.states.append(newState)
                elif len(self.states[state].transitions[symbol]) < 1: #transition for symbol leads to reject state
                    if self.rejectState == -1: #if rejectState doesn't exist, make it
                        self.rejectState = self.createState()
                        self.states[self.rejectState].stateSet = [self.rejectState]
                        for letter in self.alphabet[:-1]:
                            self.states[self.rejectState].transitions[letter] = [self.rejectState]
                        self.states[state].transitions[symbol] = [self.rejectState]
                    else:
                        self.states[state].transitions[symbol] = [self.rejectState] # set transition to rejectState
                if self.states[state].transitions[symbol] != self.states[state].stateSet: # convert transitions of state if symbol doesn't transition back to self
                    for i in range(len(self.states)):
                            if self.states[i].stateSet == self.states[state].transitions[symbol]:
                                self.NFAtoDFA(i)

    def testInputStrings(self, inputFile):
        outputFileNum = inputFile - "re" - "In.txt"
        print(outputFileNum)
        outputFile = open("re" + outputFileNum + "Out.txt", "w")
        #loop through input strings to simulate computation of DFA
        for string in self.testStrings:
            currentState = self.startState
            if (string != []): #check for empty string
                for symbol in string: #iterate through symbols of input string
                    #move states based on currentState, symbol, and transition function
                    currentState = self.states[currentState].transitions[symbol][0]
            if self.states[currentState].acceptState:
                outputFile.write("true\n")
            else:
                outputFile.write("false\n")
        outputFile.close()

#get command line input txt file and parse lines into list
cmdLine = sys.argv
inputFileName = cmdLine[1]
inputFile = open(inputFileName, "r")
lines = inputFile.readlines()
inputFile.close()

#set number of states and alphabet
alphabet = []
lineCount = 0
for symbol in lines[lineCount]:
    if symbol != '\n' and symbol != string.whitespace:
        alphabet.append(symbol)
alphabet.append('e')

#create regular expression string
lineCount += 1
line = str(lines[lineCount][:-1])
line = line.replace(' ', '') #remove whitespace from regExpr
testStrings = []

#create list of input strings to test on DFA
for string in lines[lineCount+1:]:
    testStrings.append(string[:-1])

#initialize RegexToDFA Object with alphabet, line, and testStrings
regexToDFA = RegexToDFA(alphabet, line, testStrings)

#runs regexToNFA(), setStateSets(), combineEpsilonStates(), NFAtoDFA(), and popUnusedStates()
regexToDFA.convert()

#test the input strings on the DFA
regexToDFA.testInputStrings(inputFileName)
