#!/bin/bash

for i in {1..20}
do
   echo "This is iteration $i"
   echo "Training against Greedy Bot..."
   python heads_up.py -p1 rlbot 1.0 0.8 -p2 greedy -n 1000
   echo "Training against RLBot..."
   python heads_up.py -p1 rlbot 1.0 0.8 -p2 rlbot -n 500
   echo "Evaluating Performance..."
   python heads_up.py -p
done
