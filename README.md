# ToDo List
[Google Doc Link](https://docs.google.com/document/d/1s_93HzQu_74fJWDLWwISt_NYs3OvQ41pf5nRqQ8sUA4/edit?usp=sharing).  
Please request access if you would like to change the doc or check things off.  
  

# ClockNBlock 2022 Version
Written by `@ArnavVWadhwa` and `@bvesper15` this is the new version of the clockNBlock project with the "shiny new delta arm." The major changes this year was to the circuit boards used. We added `@Stan-Reifel's` new DPi Circuit boards and redid the wiring. 
  
The code is also completely brand new and this is the third version of the code I have written. I hope it holds up to a good standard.

For any questions with the project feel free to reach out me.  
Arnav Wadhwa:  
(805) 570-5030.   
arnav.v.wadhwa@gmail.com

Note: When you contact me please let me know who you are and that this is for the clock and block so I don't accidently ignore you.

Here is the fun story for the project.
# It Clocks! It Blocks! New and improved only at Faker Maire!

# A Tale of Two Arms

This is the repository for the redesigned ClockNBlocks. The ClockNBlocks is a project in which a robotic arm stacks block towers, and sweeping clock hands susequently knock over the towers.

The project was first developed in the 2016-17 school year, employing a gantry-style serial manipulator arm. It wasn't fast; it wasn't elegant, but in ran like a beauty. The code for this version of the project was perfected by `@jproney` himself in the fall of 2017, and can be found here: https://github.com/dpengineering/ClockNBlockHW

After `@jproney's` labors to perfect the CNB, the original project was torn apart, and the slow, sturdy gantry arm replaced with a shiny new Delta Robot. What is a Delta Robot you ask? Luckily for you, `@jproney` made https://github.com/dpengineering/DeltaArm to answer this age old question. The DeltaArm repository contains the Inverse Kinematic and Forward Kinematic equations for controlling the new Delta Arm.

But that's not where the story ends. The original ClockNBlock was powered by an artificial brain known as the R-dwino (sometimes stylized _Arduino_). However, the new arm was to be controlled by a Pi of Raspberry and it's trusty companion, the Engine of Slush. Therefore, it became necessary for the Arduinos controlling the project's pneumatic actuators to communicate with the Rasperry Pi. To accomplish this task, `@jproney` created https://github.com/dpengineering/PythonManager by standing of the shoulders of `@jmgrosen`, the hero who first brought peace to Mechatronica. Unfortunately,
PythonManager was developed quite hastily, and is currently rather messy and confusing. 

And now that brings us here. The repository you are viewing combines the DeltaArm, PythonManager, and old ClockNBlockHW repositiories to create ClockNBlockPi. In its current state, the ClockNBlock runs, but not well. The arm control software (forward/inverse kinematics) works quite well, but for one reason or another the arm struggles to maintain the sub-inch precision required to pick up blocks consistently. This is likely due to backlash in the arm transmissions, slippage in shaft couplers, and inconsistencies in the homing of the arm.

Now you come into the story, young squire. Your task is to tame the Arm of Delta, build the Block Towers high once more, and bring the ClockNBlock back to its golden age. Godspeed.

Sincerely,
James "Petey/Stagflation/jproney" Roney

P.S. I did most (all) of these - Arnav
