# Report

Team members:

- Sofya Aksenyuk, 150284
- Uladzimir Ivashka, 150281

## Problem Description

Given a set of nodes, each characterized by their (x, y) coordinates in a plane and an associated cost, the challenge is to select exactly 50% of these nodes and form a Hamiltonian cycle. 

The goal is to minimize the sum of the total length of the path plus the total cost of the selected nodes. 

Distances between nodes are computed as Euclidean distances and rounded to the nearest integer. 

## Methodology

### Steepest Local Search with the use of move evaluations (deltas) from previous iterations

Steepest Local Search systematically examines all possible moves within the neighborhood, both intra-route and inter-route, and selects the move that results in the best improvement in the objective function value. 

It aims to find the absolute best move at each step.

Steepest Local Search with Move Evaluations begins with an initial solution and iteratively explores neighboring solutions to identify potential moves. 

During each iteration, the algorithm explores neighboring solutions and calculates the delta for each move. 

By evaluating the moves in this manner, the algorithm can prioritize and select the most promising moves that lead to improvements in solution quality.

The use of move evaluations from previous iterations allows the algorithm to adapt its search strategy based on the historical performance of moves. 

Moves that have previously demonstrated a positive impact on solution quality are given higher priority, guiding the search towards more promising regions of the solution space.


## Source code

Link: [Source Code](https://github.com/aksenyuk/evolutionary-computation/blob/main/previous-iterations-deltas-local-search/previous-iterations-deltas-local-search.ipynb)

<div style="page-break-after: always"></div>

## Pseudocode

### Steepest Local Search with the use of move evaluations (deltas) from previous iterations

    FUNCTION SteepestLocalSearchDeltas(Solution, DistanceMatrix, Costs)

        LM = SortedSet() // to store moves and their deltas
        Calculate the size of the solution and the total number of nodes
        Improved = True

        WHILE (Improved is True):
            Improved = False

            // Inter moves
            FOR each Move in combination of inner node and outer node: 
                Delta = (calculate delta for inter move)
                IF (Delta > 0): //brings improvement
                    LM.add((Delta, Move, MoveInfo))

            // Intra moves
            FOR each Move in combination of two edges in solution:
                Delta = (calculate delta for intra edge move)
                IF (Delta > 0): //brings improvement
                    LM.add((Delta, Move, MoveInfo))

            // Process LM
            FOR each Move in LM:
                ToApply, ToStore = CheckMoveValidity(Solution, Move)
                IF (ToApply is True):
                    Improved = True
                    Solution = (apply move)
                    LM.remove(Move) // move is made, remove it
                ELSE IF (ToStore is not True):
                    LM.remove(Move) // move is no valid
                IF Improved:
                    Break loop // if move already found and made

        RETURN solution

<div style="page-break-after: always"></div>

    FUNCTION CheckMoveValidity(Solution, Move)
        Decompose Move into MoveType, MoveNodes, and AdjacentNodes

        IF (MoveType == 'inter'):
            ExternalNode, InternalNode = MoveNodes
            AdjacentNodePrev, AdjacentNodeNext = AdjacentNodes

            IF (InternalNode in Solution and ExternalNode not in Solution):
                // Check existence and order of edges involving InternalNode
                EdgePrevExists = ((AdjacentNodePrev, InternalNode) forms an edge in correct order in Solution)
                EdgeNextExists = ((InternalNode, AdjacentNodeNext) forms an edge in correct order in Solution)
                RETURN (EdgePrevExists and EdgeNextExists, not (EdgePrevExists and EdgeNextExists))
            ELSE:
                RETURN (False, False)

        IF (MoveType == 'intra'):
            Node1, Node2 = MoveNodes
            AdjacentNode1, AdjacentNode2 = AdjacentNodes

            // Check existence and order of edges for intra move
            Edge1Exists = ((Node1, AdjacentNode1) forms an edge in correct order in Solution)
            Edge2Exists = ((Node2, AdjacentNode2) forms an edge in correct order in Solution)
            RETURN (Edge1Exists and Edge2Exists, not (Edge1Exists and Edge2Exists))

<div style="page-break-after: always"></div>

# Computational Experiments

## Results

### Table of Cost

<img src="plots/costs.png"/>

### Table of Time

<img src="plots/times.png"/>

## Best Solutions Plots

See plots: [Plots](https://github.com/aksenyuk/evolutionary-computation/tree/main/previous-iterations-deltas-local-search/plots/)

<div style="page-break-after: always"></div>

<img src="plots/Steepest-PreviousDeltas-Random.png"/>

<div style="page-break-after: always"></div>

# Best solution among all methods so far

## TSPA

[42, 89, 94, 12, 72, 190, 98, 66, 156, 6, 24, 141, 144, 87, 79, 194, 21, 171, 154, 81, 62, 108, 15, 117, 53, 22, 195, 55, 36, 132, 128, 25, 181, 113, 74, 163, 61, 71, 20, 64, 185, 96, 27, 116, 147, 59, 143, 159, 164, 178, 19, 0, 149, 50, 121, 91, 114, 4, 77, 43, 192, 175, 153, 88, 127, 186, 45, 167, 101, 60, 126, 174, 199, 41, 177, 1, 75, 189, 109, 130, 152, 11, 48, 106, 26, 119, 134, 99, 135, 51, 5, 112, 73, 31, 95, 169, 8, 80, 14, 111]

**Cost:** 74541.0

## TSPB
    
[158, 162, 150, 44, 117, 196, 192, 21, 142, 130, 174, 51, 91, 70, 140, 148, 141, 53, 69, 115, 82, 63, 8, 14, 16, 172, 95, 163, 182, 2, 5, 34, 183, 197, 179, 31, 101, 42, 38, 103, 131, 121, 24, 127, 143, 122, 92, 26, 66, 169, 99, 50, 154, 134, 25, 36, 165, 37, 137, 88, 55, 4, 153, 145, 157, 80, 57, 0, 135, 198, 190, 19, 29, 33, 136, 61, 73, 185, 132, 18, 52, 12, 107, 139, 193, 119, 59, 71, 166, 85, 64, 147, 159, 89, 129, 58, 171, 72, 114, 67]

**Cost:** 68122.0

## TSPC
    
[81, 171, 108, 62, 15, 117, 53, 22, 55, 195, 74, 163, 113, 132, 128, 40, 164, 178, 19, 35, 69, 0, 149, 50, 121, 91, 114, 175, 2, 4, 77, 43, 192, 150, 199, 39, 174, 137, 41, 177, 1, 75, 189, 109, 130, 152, 11, 160, 106, 48, 92, 26, 119, 134, 139, 95, 169, 110, 8, 80, 31, 73, 89, 42, 94, 12, 72, 98, 156, 172, 6, 66, 190, 112, 5, 51, 135, 99, 101, 9, 60, 167, 153, 88, 127, 45, 186, 170, 129, 157, 21, 194, 79, 87, 141, 144, 102, 44, 133, 154]

**Cost:** 50972.0

## TSPD
    
[87, 147, 159, 64, 129, 89, 58, 171, 72, 114, 85, 166, 28, 59, 119, 193, 71, 44, 162, 150, 117, 196, 192, 21, 138, 142, 130, 161, 174, 188, 140, 148, 141, 53, 96, 32, 113, 69, 115, 82, 63, 8, 14, 84, 139, 97, 107, 12, 52, 132, 18, 16, 172, 95, 19, 190, 198, 135, 128, 66, 169, 0, 57, 99, 92, 122, 143, 179, 121, 127, 24, 50, 112, 154, 134, 25, 36, 194, 123, 165, 37, 146, 137, 88, 55, 4, 153, 80, 157, 145, 79, 136, 61, 73, 185, 47, 189, 170, 181, 187]

**Cost:**  46915.0

<div style="page-break-after: always"></div>

# Conclusions

## Cost Comparison

Among all TSP instances Steepest-PreviousDeltas-Random method shows __slightly__ higher costs than Steepest-edges-Random

## Time Efficiency

A notable reduction in computation time is observed with Steepest-PreviousDeltas-Random across all TSP instances when compared to Steepest-edges-Random

This reduction aligns with the goal of improving time efficiency through the use of move evaluations from previous iterations

However, it still takes much longer in comparison with Steepest-CandidateMovesEdges-Random

