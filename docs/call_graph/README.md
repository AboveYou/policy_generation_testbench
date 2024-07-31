# Call Graph
A small sample written to demonstrate the creation of call graphs via LLVM. The output can be found in the paper.

## Requirements
```bash
dnf install llvm clang graphviz
```

## How to run?
```bash
# compile into LLVM IR
clang -emit-llvm -o call_graph.bc -c call_graph.c 

# create the call graph
opt -passes=dot-callgraph call_graph.bc 

# create the image
dot -T png call_graph.bc.callgraph.dot -o call_graph.png -Glabel=""    
```