# A very short introduction

This repository explores DFA learning solutions. DFA learning from examples is supposed to be hard, because it's a known NP-hard problem in general, unless the training samples follow a very restrictive format. 
In this project, we aim to follow the algorithmic framework as introduced in the final report of Abbadingo One competition as published in ICGI-98 (https://abbadingo.cs.nuim.ie/). 
The first greedy strategy was implemented in dfa-greedy-merge.py as a proof of concept, which is currently tested with small DFA representations, running on a Linux desktop with about 32GB memory space. Later we will try cases similar to the practice problems of Abadingo One.

- **project target**

We aim to develop a more sophisticated toolkit for (minimum-state) DFA learning with a standardised I/O format and components such as heuristic merging, compatibility test, randomization, DFA minimization, and operations on DFA that we have not yet thought of.
We will later explore and compare our approach with other solutions, such as those used in Abbadingo One competition and those by reduction to a SAT-solver.


