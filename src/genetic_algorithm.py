import random
from deap import base, creator, tools
import numpy as np
import pandas as pd


def otimizar_roteiro_ag(
    df_cidades,
    pesos_usuario,
    num_dias=10,
    orcamento_total=1500,
    pop_size=100,
    generations=40,
):
    num_cidades_selecionar = max(3, num_dias // 2)
    cidades_list = df_cidades.to_dict("records")
    total_disponivel = len(cidades_list)

    if hasattr(creator, "FitnessMax"):
        del creator.FitnessMax
    if hasattr(creator, "Individual"):
        del creator.Individual

    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMax)

    toolbox = base.Toolbox()
    toolbox.register(
        "indices", random.sample, range(total_disponivel), num_cidades_selecionar
    )
    toolbox.register(
        "individual", tools.initIterate, creator.Individual, toolbox.indices
    )
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    def avaliar(individual):
        cidades_ind = [cidades_list[i] for i in individual]
        dias_por_cidade = num_dias / len(individual)
        custo_hospedagem = (
            sum(c["custo_diario_eur"] for c in cidades_ind) * dias_por_cidade
        )
        custo_deslocamento = (len(individual) - 1) * 80
        custo_total = custo_hospedagem + custo_deslocamento

        soma_pesos = sum(pesos_usuario.values())
        score_base = sum(
            (c["cultura_historia"] * pesos_usuario["cultura"])
            + (c["gastronomia_vibe"] * pesos_usuario["vibe"])
            + (c["infra_seguranca"] * pesos_usuario["infra"])
            + (c["conectividade"] * pesos_usuario["conectividade"])
            for c in cidades_ind
        ) / (len(individual) * soma_pesos)

        penalidade = 0
        if custo_total > orcamento_total:
            penalidade = (custo_total - orcamento_total) * 0.1

        fitness = (score_base * 10) - penalidade
        return (max(0, fitness),)

    def cruzamento(ind1, ind2):
        set1, set2 = set(ind1), set(ind2)
        comuns = list(set1.intersection(set2))
        restantes = list(set1.symmetric_difference(set2))
        random.shuffle(restantes)
        filho1 = comuns + restantes[: len(ind1) - len(comuns)]
        filho2 = comuns + restantes[len(ind1) - len(comuns) :]
        return creator.Individual(filho1), creator.Individual(filho2)

    def mutacao(individual):
        idx_troca = random.randint(0, len(individual) - 1)
        disponiveis = list(set(range(total_disponivel)) - set(individual))
        if disponiveis:
            individual[idx_troca] = random.choice(disponiveis)
        return (individual,)

    toolbox.register("evaluate", avaliar)
    toolbox.register("mate", cruzamento)
    toolbox.register("mutate", mutacao)
    toolbox.register("select", tools.selTournament, tournsize=3)

    pop = toolbox.population(n=pop_size)

    for g in range(generations):
        offspring = toolbox.select(pop, len(pop))
        offspring = list(map(toolbox.clone, offspring))

        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < 0.7:
                toolbox.mate(child1, child2)
                del child1.fitness.values
                del child2.fitness.values

        for mutant in offspring:
            if random.random() < 0.2:
                toolbox.mutate(mutant)
                del mutant.fitness.values

        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        pop[:] = offspring

    melhor_ind = tools.selBest(pop, 1)[0]
    roteiro_otimizado = df_cidades.iloc[melhor_ind].copy()
    return roteiro_otimizado, melhor_ind.fitness.values[0]