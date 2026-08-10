import numpy as np
import random
import math
from typing import List, Tuple, Dict, Any

np.random.seed(42)
random.seed(42)

def generate_mock_farms(num_farms: int, grid_size: int = 100) -> Tuple[np.ndarray, np.ndarray]:
    coords = np.random.rand(num_farms, 2) * grid_size
    dist_matrix = np.zeros((num_farms, num_farms))

    for i in range(num_farms):
        for j in range(num_farms):
            if i != j:
                dist_matrix[i][j] = np.linalg.norm(coords[i] - coords[j])
    return coords, dist_matrix

def calculate_fitness(chromosome: List[int], dist_matrix: np.ndarray, num_vehicles: int) -> float:
    """
    تابع برازش برای mTSP: شکستن کروموزوم به K بخش (کمباین)
    و محاسبه زمان طولانی‌ترین مسیر (Makespan).
    """
    chunk_size = math.ceil(len(chromosome) / num_vehicles)
    routes = [chromosome[i:i + chunk_size] for i in range(0, len(chromosome), chunk_size)]
    
    makespan = 0
    total_dist = 0
    
    for route in routes:
        if not route: continue
        # شروع از گاراژ (نود 0)
        dist = dist_matrix[0][route[0]]
        for i in range(len(route)-1):
            dist += dist_matrix[route[i]][route[i+1]]
        # بازگشت به گاراژ
        dist += dist_matrix[route[-1]][0]
        
        if dist > makespan:
            makespan = dist
        total_dist += dist
        
    # کمینه کردن ماکزیمم مسافت (زمان‌بندی) + کسر کوچکی از مسافت کل برای بهینگی مسیر
    return makespan + (0.001 * total_dist)

def tournament_selection(population: List[List[int]], fitness_scores: List[float], k: int = 3) -> List[int]:
    selected_indices = random.sample(range(len(population)), k)
    best_idx = min(selected_indices, key=lambda idx: fitness_scores[idx])
    return population[best_idx]

def order_crossover(parent1: List[int], parent2: List[int]) -> List[int]:
    size = len(parent1)
    start, end = sorted(random.sample(range(size), 2))
    child = [-1] * size
    child[start:end+1] = parent1[start:end+1]
    p2_genes = [gene for gene in parent2 if gene not in child]
    idx = 0
    for i in range(size):
        if child[i] == -1:
            child[i] = p2_genes[idx]
            idx += 1
    return child

def swap_mutation(chromosome: List[int], mutation_rate: float) -> List[int]:
    mutated = chromosome.copy()
    if random.random() < mutation_rate:
        idx1, idx2 = random.sample(range(len(mutated)), 2)
        mutated[idx1], mutated[idx2] = mutated[idx2], mutated[idx1]
    return mutated

def solve_harvester_routing(
    num_farms: int = 15,
    num_vehicles: int = 3,
    generations: int = 200,
    pop_size: int = 100,
    mutation_rate: float = 0.15,
    early_stopping_patience: int = 30
) -> Dict[str, Any]:
    
    coords, dist_matrix = generate_mock_farms(num_farms)
    
    # در mTSP، نود 0 گاراژ است، پس مزارع از 1 تا N-1 هستند
    farms = list(range(1, num_farms))
    population = [list(np.random.permutation(farms)) for _ in range(pop_size)]

    history_best_distances = []
    global_best_path = None
    global_best_distance = float('inf')
    generations_without_improvement = 0

    for gen in range(generations):
        fitness_scores = [calculate_fitness(ind, dist_matrix, num_vehicles) for ind in population]
        current_best_dist = min(fitness_scores)
        current_best_idx = fitness_scores.index(current_best_dist)

        if current_best_dist < global_best_distance:
            global_best_distance = current_best_dist
            global_best_path = population[current_best_idx].copy()
            generations_without_improvement = 0
        else:
            generations_without_improvement += 1

        history_best_distances.append(global_best_distance)

        if generations_without_improvement >= early_stopping_patience:
            break

        new_population = [global_best_path]

        while len(new_population) < pop_size:
            parent1 = tournament_selection(population, fitness_scores, k=3)
            parent2 = tournament_selection(population, fitness_scores, k=3)
            child = order_crossover(parent1, parent2)
            child = swap_mutation(child, mutation_rate)
            new_population.append(child)

        population = new_population

    return {
        "best_path": global_best_path,
        "best_distance": round(global_best_distance, 2), # این الان Makespan است
        "history": history_best_distances,
        "coords": coords.tolist(),
        "stopped_at_generation": gen,
        "num_vehicles": num_vehicles
    }
