import random
import numpy as np
import operator
import matplotlib.pyplot as plt

from deap import base, benchmarks, creator, tools

creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Particle", list, fitness=creator.FitnessMin, speed=list, smin=None, smax=None, best=None)
toolbox = base.Toolbox()
#  number of generations
GEN = 0  # type: int
#  population size
POP_SIZE = 0  # type: int
#  particle dimension size
DIM_SIZE = 0
current_dim = 0
current_particle = 0
current_gen = 0

#MAPS for holding chaotic values
Map1 = []
Map2 = []


def LogisticMap(xn):
    r = 4.  # r is the chaos growth rate
    return r * xn * (1. - xn)


#  Change each element inside the MAP to next chaotic value
def chaoticFunc(MAP):
    for i in range(POP_SIZE):
        for j in range(DIM_SIZE):
            MAP[i][j] = LogisticMap(MAP[i][j])
    return MAP


def save_data(file_name, average_mins, problem_type):
    file = open("output/" + problem_type+"/"+ file_name + ".dat", 'w')
    for record in average_mins:
        file.write(str(record) + "\n")
    file.close()


def generate(size, pmin, pmax, smin, smax):
    global chaos1, chaos2, current_part_generate

    part = creator.Particle(random.uniform(pmin, pmax) for _ in range(size))
    part.speed = [random.uniform(smin, smax) for _ in range(size)]
    part.smin = smin
    part.smax = smax
    return part


def updateParticle(part, best, phi1, phi2):
    global current_particle

    # get dimension values for specific current particle in MAP1,2
    temp_chaos1 = Map1[current_particle][:]
    temp_chaos2 = Map2[current_particle][:]

    # assign them as the new random variables
    u1 = (temp_chaos1[i]*phi1 for i in range(len(part)))
    u2 = (temp_chaos2[i]*phi2 for i in range(len(part)))
    v_u1 = map(operator.mul, u1, map(operator.sub, part.best, part))
    v_u2 = map(operator.mul, u2, map(operator.sub, best, part))
    part.speed = list(map(operator.add, part.speed, map(operator.add, v_u1, v_u2)))
    for i, speed in enumerate(part.speed):
        if speed < part.smin:
            part.speed[i] = part.smin
        elif speed > part.smax:
            part.speed[i] = part.smax
    part[:] = list(map(operator.add, part, part.speed))

    #  Increase particle index
    current_particle += 1


def main():
    global current_gen, Map1, Map2, current_particle, current_part_generate
    pop = toolbox.population(n=POP_SIZE)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean)
    stats.register("std", np.std)
    stats.register("min", np.min)
    stats.register("max", np.max)

    logbook = tools.Logbook()
    logbook.header = ["gen", "evals"] + stats.fields

    best = None
    # map[:, i] = appli
    # CHAOTIC MAP GENERATOR
    # MAP = np.ndarray(shape=(POP_SIZE, DIMENSION), dtype=float, order='F')
    # Initial MAP contains all randoms with PARTxDIM
    Map1 = [[random.uniform(0, 1.) for _ in range(DIM_SIZE)] for _ in range(POP_SIZE)]
    Map2 = [[random.uniform(0, 1.) for _ in range(DIM_SIZE)] for _ in range(POP_SIZE)]
    current_gen = 0
    for g in range(GEN):
        current_particle = 0

        for part in pop:
            part.fitness.values = toolbox.evaluate(part)
            if not part.best or part.best.fitness < part.fitness:
                part.best = creator.Particle(part)
                part.best.fitness.values = part.fitness.values
            if not best or best.fitness < part.fitness:
                best = creator.Particle(part)
                best.fitness.values = part.fitness.values
        for part in pop:
            toolbox.update(part, best)
        logbook.record(gen=g, evals=len(pop), **stats.compile(pop))

        # Update maps with next chaotic level
        Map1 = chaoticFunc(Map1)
        Map2 = chaoticFunc(Map2)
        current_gen += 1

    return pop, logbook, best


# CALL THIS FUNCTION FROM OUTSIDE OF THE SCRIPT
def logistic_cluster_run(generation, particle, dimension, experiment, problem_type, PHI1, PHI2, SMIN, SMAX, PMIN, PMAX):
    global GEN, POP_SIZE, EXPERIMENT, DIM_SIZE, toolbox, current_dim, current_part_generate
    print("LogisticPSO has started solving " + problem_type.swapcase() + " problem with number of generations: "+str(generation)+", population size: "+str(particle)+", particle dimension: "+str(dimension)+" with experiment size of "+str(experiment))
    GEN = generation
    POP_SIZE = particle
    EXPERIMENT = experiment
    DIM_SIZE = dimension

    # Register parameters
    toolbox.register("particle", generate, size=DIM_SIZE, pmin=PMIN, pmax=PMAX, smin=SMIN, smax=SMAX)
    toolbox.register("population", tools.initRepeat, list, toolbox.particle)
    toolbox.register("update", updateParticle, phi1=PHI1, phi2=PHI2)
    # Register selected problem
    if problem_type == "sphere":
        toolbox.register("evaluate", benchmarks.sphere)
    elif problem_type == "griewank":
        toolbox.register("evaluate", benchmarks.griewank)
    elif problem_type == "rastrigin":
        toolbox.register("evaluate", benchmarks.rastrigin)
    elif problem_type == "schaffer":
        toolbox.register("evaluate", benchmarks.schaffer)
    elif problem_type == "rosenbrock":
        toolbox.register("evaluate", benchmarks.rosenbrock)
    elif problem_type == "schwefel":
        toolbox.register("evaluate", benchmarks.schwefel)
    elif problem_type == "ackley":
        toolbox.register("evaluate", benchmarks.ackley)
    elif problem_type == "himmelblau":
        toolbox.register("evaluate", benchmarks.himmelblau)

    # number of experiments
    average_mins = [0.] * GEN
    for r in range(EXPERIMENT):
        pop, logbook, best = main()
        print(logbook.select("min"))
        gen = logbook.select("gen")
        fit_mins = logbook.select("min")
        for i in range(GEN):
            average_mins[i] += fit_mins[i] / EXPERIMENT

    file_name = "logistic_results"
    #save_data(file_name, average_mins, problem_type)

    # plt.title(problem_type.swapcase())
    # plt.xlabel("Generation")
    # plt.ylabel("Minimum Fitness")
    # plt.plot(gen, average_mins)
    # plt.show()


if __name__ == '__main__':
    logistic_cluster_run(500, 50, 100, 30, "griewank")
