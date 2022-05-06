# Verilog To Dimacs

A Python file that take in a Verilog file, the number of times the user wants to unroll the Verilog file, and the desired state, and translates the Verilog file into the proper DIMACS file. This created DIMACS file is then run in the Satisfiability Solver(SAT) MINISAT where the desired reachable state is determined to be reachable (Satisfied) or unreachable (unsatisfied) in the number of unrollings given by the user.
