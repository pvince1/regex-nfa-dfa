# regex-nfa-dfa
Converts regular expression to nfa to dfa and test if input strings exist in regular language

Files:
README.md
pa3.py
reIn1.txt #example input files for testing and format
reIn5.txt
reIn10.txt
 
Python script pa3.py takes in an input file containing:
-alphabet of regular language
-regular expression (e.g. 1*(01|10) )
-input strings to test

Classes:
-StateSet: represents state in nfa/dfa
  attributes: acceptState, used, stateSet, transitions
-RegexToDFA: main class converts regex to nfa to dfa and test strings
  methods:
    - __init__()
    - convert()
    - regexToNFA()
    - combineEndStates()
    - setStateSets()
    - combineEpsilonStates()
    - NFAtoDFA()
    


