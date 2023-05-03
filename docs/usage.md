# Usage

### Spark Notes:
To run the machine, turn it on and if there are blocks
in the entrance of all the feeders, it will run in personality mode, otherwise it will
run in the regular mode.

### File Structure:  

The project is structured like this:  
```
startup.py 
imbuingPersonality/
    main.py
    *Other files*

regularMoves/
    main.py
    *Other files*
```
startup.py will choose which version of the code to run.  
Currently, this file is stored within this repo, the structure
looks like the one above on the RPi though.  

### Running the machine:
Basically just watch it do its thing, if anything scary happens or a catastrophic failure happens,
press the big red E-STOP button and swear at me. I hope this never happens.