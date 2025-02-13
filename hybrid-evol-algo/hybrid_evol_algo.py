import argparse
import random
import time
import warnings
from itertools import combinations, product

import numpy as np
import pandas as pd
from scipy.spatial.distance import pdist, squareform

warnings.filterwarnings("ignore")


def get_distance_matrix(df):
    coords = df[["x", "y"]].to_numpy()

    distance_matrix = np.round(squareform(pdist(coords, "euclidean")))
    np.fill_diagonal(distance_matrix, 0)

    return distance_matrix


def random_search(distance_matrix):
    n = len(distance_matrix)

    solution = list(range(n))
    np.random.shuffle(solution)

    return solution[: (n // 2)]


def get_total_cost(solution, distance_matrix, costs):
    assert len(solution) * 2 == len(distance_matrix)
    total_cost = 0

    for i in range(len(solution) - 1):
        total_cost += (
            distance_matrix[solution[i], solution[i + 1]] + costs[solution[i + 1]]
        )

    total_cost += distance_matrix[solution[-1], solution[0]] + costs[solution[0]]

    return total_cost


def compute_inter_move_delta(solution, distance_matrix, costs, idx, new_node):
    n = len(solution)
    new_solution = solution.copy()
    old_node = solution[idx]

    new = (
        costs[new_node]
        + distance_matrix[new_solution[idx - 1], new_node]
        + distance_matrix[new_node, new_solution[(idx + 1) % n]]
    )

    old = (
        costs[old_node]
        + distance_matrix[new_solution[idx - 1], old_node]
        + distance_matrix[old_node, new_solution[(idx + 1) % n]]
    )

    delta = new - old
    new_solution[idx] = new_node

    return new_solution, delta


def compute_intra_move_delta(solution, distance_matrix, indices, backward=False):
    ## without roll/shift to initial form
    n = len(solution)
    i, j = indices

    if i >= j:
        raise Exception("Wrong indices, i >= j")
    if j >= n:
        raise Exception("Wrong indices, j >= n")

    if backward:
        if (i == 0 and j in (n - 1, n - 2)) or (j == n - 1 and i in (0, 1)):
            return solution, 0
        new = (
            distance_matrix[solution[i], solution[(j + 1) % n]]
            + distance_matrix[solution[j], solution[i - 1]]
        )
        old = (
            distance_matrix[solution[i - 1], solution[i]]
            + distance_matrix[solution[j], solution[(j + 1) % n]]
        )
    else:
        if j - i in (1, 2):
            return solution, 0
        new = (
            distance_matrix[solution[i], solution[j - 1]]
            + distance_matrix[solution[i + 1], solution[j]]
        )
        old = (
            distance_matrix[solution[i], solution[i + 1]]
            + distance_matrix[solution[j - 1], solution[j]]
        )

    delta = new - old

    if backward:
        new_solution = (
            solution[j + 1 :][::-1] + solution[i : j + 1] + solution[:i][::-1]
        )
    else:
        new_solution = solution[: i + 1] + solution[i + 1 : j][::-1] + solution[j:]

    return new_solution, delta


def steepest_local_search(solution, distance_matrix, costs):
    solution = solution[:]
    n, N = len(solution), len(distance_matrix)
    solution_set = set(solution)
    outer_nodes_set = set(range(N)) - solution_set

    while True:
        best_delta, best_solution = 0, None
        inter_move_flag, inter_move_outer_node, inter_move_inner_node_idx = (
            False,
            None,
            None,
        )

        # inter
        for outer_node, inner_node_idx in product(outer_nodes_set, range(n)):
            new_solution, delta = compute_inter_move_delta(
                solution, distance_matrix, costs, inner_node_idx, outer_node
            )
            if delta < best_delta:
                best_delta = delta
                best_solution = new_solution[:]
                inter_move_flag = True
                inter_move_outer_node, inter_move_inner_node_idx = (
                    outer_node,
                    inner_node_idx,
                )

        # intra
        for i, j in combinations(range(n), 2):
            # forward
            new_solution, delta = compute_intra_move_delta(
                solution, distance_matrix, (i, j), False
            )
            if delta < best_delta:
                best_delta = delta
                best_solution = new_solution[:]
                inter_move_flag = False
            # backward
            new_solution, delta = compute_intra_move_delta(
                solution, distance_matrix, (i, j), True
            )
            if delta < best_delta:
                best_delta = delta
                best_solution = new_solution[:]
                inter_move_flag = False

        if best_solution is not None:
            if inter_move_flag:
                solution_set.add(inter_move_outer_node)
                solution_set.remove(solution[inter_move_inner_node_idx])
                outer_nodes_set.remove(inter_move_outer_node)
                outer_nodes_set.add(solution[inter_move_inner_node_idx])
            solution = best_solution[:]
            continue
        return solution


def greedy_2_regret_weighted(
    distance_matrix, partial_solution, costs, target_size, regret_weight=0.5
):
    num_nodes = len(distance_matrix)
    to_visit = set(range(num_nodes)) - set(partial_solution)

    solution = partial_solution[:]

    while len(solution) < target_size:
        max_weighted_sum = float("-inf")
        best_node = None
        best_insertion_point = None

        for node in to_visit:
            insertion_costs = []
            for i in range(len(solution) - 1):
                cost = (
                    distance_matrix[solution[i]][node]
                    + distance_matrix[node][solution[i + 1]]
                    - distance_matrix[solution[i]][solution[i + 1]]
                    + costs[node]
                )
                insertion_costs.append((cost, i))

            insertion_costs.append(
                (
                    distance_matrix[solution[-1]][node]
                    + distance_matrix[node][solution[0]]
                    - distance_matrix[solution[-1]][solution[0]]
                    + costs[node],
                    len(solution) - 1,
                )
            )

            insertion_costs.sort(key=lambda x: x[0])

            weighted_sum = 0
            if len(insertion_costs) > 1:
                regret = insertion_costs[1][0] - insertion_costs[0][0]
                objective = -insertion_costs[0][0]
                weighted_sum = regret_weight * regret + (1 - regret_weight) * objective

            if weighted_sum > max_weighted_sum:
                max_weighted_sum = weighted_sum
                best_node = node
                best_insertion_point = insertion_costs[0][1]

        solution.insert(best_insertion_point + 1, best_node)
        to_visit.remove(best_node)

    return solution


def get_initial_population(pop_size, distance_matrix, costs):
    population = []
    for _ in range(pop_size):
        solution = random_search(distance_matrix)
        new_solution = steepest_local_search(solution, distance_matrix, costs)
        population.append(new_solution)
    return population


def operator_1(parent1, parent2):
    length = len(parent1)
    child = [None] * length

    edges1 = {
        tuple(sorted((parent1[i], parent1[(i + 1) % length]))) for i in range(length)
    }
    edges2 = {
        tuple(sorted((parent2[i], parent2[(i + 1) % length]))) for i in range(length)
    }
    common_edges = edges1.intersection(edges2)

    for i in range(length - 1):
        edge = tuple(sorted((parent1[i], parent1[i + 1])))
        if edge in common_edges:
            child[i] = parent1[i]
            child[i + 1] = parent1[i + 1]

    common_nodes = set(parent1) & set(parent2) - set(child)

    for node in common_nodes:
        for i in range(length):
            if child[i] is None:
                child[i] = node
                break

    remaining_nodes = [node for node in range(length * 2) if node not in child]
    random.shuffle(remaining_nodes)
    for i in range(length):
        if child[i] is None:
            child[i] = remaining_nodes.pop()

    return child


def operator_2(parent1, parent2, distance_matrix, costs):
    length = len(parent1)

    edges1 = {
        tuple(sorted((parent1[i], parent1[(i + 1) % length]))) for i in range(length)
    }
    edges2 = {
        tuple(sorted((parent2[i], parent2[(i + 1) % length]))) for i in range(length)
    }
    common_edges = edges1.intersection(edges2)

    modified_parent = []
    for i in range(length - 1):
        edge = tuple(sorted((parent1[i], parent1[i + 1])))
        if edge in common_edges:
            if not modified_parent or modified_parent[-1] != parent1[i]:
                modified_parent.append(parent1[i])
            modified_parent.append(parent1[i + 1])

    modified_parent = greedy_2_regret_weighted(
        distance_matrix, modified_parent, costs, length
    )

    return modified_parent


def evol_algo(instance, end_time, oper_num):
    start = time.time()

    df = pd.read_csv(f"./data/{instance}.csv", sep=";", names=["x", "y", "cost"])
    costs = df.cost.to_numpy()
    distance_matrix = get_distance_matrix(df)

    population = get_initial_population(20, distance_matrix, costs)
    total_costs = [
        get_total_cost(solution, distance_matrix, costs) for solution in population
    ]

    counter = 0
    while time.time() - start < end_time:
        counter += 1
        parent1, parent2 = random.sample(population, 2)

        if oper_num == "1":
            child = operator_1(parent1, parent2)
            # child = steepest_local_search(child, distance_matrix, costs)
        elif oper_num == "2":
            child = operator_2(parent1, parent2, distance_matrix, costs)
            child = steepest_local_search(child, distance_matrix, costs)
        else:
            raise ValueError("ti huesos")

        child_total_cost = get_total_cost(child, distance_matrix, costs)

        if child_total_cost in total_costs:
            continue

        max_total_cost = max(total_costs)
        if child_total_cost > max_total_cost:
            continue

        max_total_cost_idx = total_costs.index(max_total_cost)
        total_costs[max_total_cost_idx] = child_total_cost
        population[max_total_cost_idx] = child

    best_total_cost = min(total_costs)
    best_solution = population[total_costs.index(best_total_cost)]
    return best_total_cost, best_solution, counter


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--oper")
    parser.add_argument("--instance")
    args = parser.parse_args()

    oper_num = args.oper
    instance = args.instance

    end_times = {"TSPA": 1264, "TSPB": 1310, "TSPC": 1267, "TSPD": 1269}
    # end_times = {"TSPA": 200, "TSPB": 200, "TSPC": 200, "TSPD": 200}

    times = []
    costs = []
    counters = []
    solutions = []

    for _ in range(20):
        start = time.perf_counter()
        total_cost, solution, counter = evol_algo(
            instance, end_times[instance], oper_num
        )
        end = time.perf_counter()
        total_time = end - start

        times.append(total_time)
        costs.append(total_cost)
        counters.append(counter)
        solutions.append(solution)

    with open("results/results.txt", "a+") as file:
        text_to_append = f"{instance} / {oper_num} / {np.mean(costs)} ({np.min(costs)} - {np.max(costs)}) / {np.mean(times)} ({np.min(times)} - {np.max(times)}) / {np.mean(counters)} ({np.min(counters)} - {np.max(counters)}) / {solutions[costs.index(min(costs))]}\n"  # noqa: E501

        file.write(text_to_append)


if __name__ == "__main__":
    main()
