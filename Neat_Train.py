# Import ---------------------------------------------------
import neat
import neat.nn.recurrent
from Simulation import Simulation
from concurrent.futures import ProcessPoolExecutor, as_completed
import pickle
# ----------------------------------------------------------


# Fonction -------------------------------------------------
def evaluate_single_genome(genome_id, genome, config):
    net = neat.nn.recurrent.RecurrentNetwork.create(genome, config)
    sim = Simulation(sim_id=genome_id, nn=net, init_money=10000, path_hist_data='Input_Data\\DF_ETHUSDT_15m.csv')
    return genome_id, sim.start()  # retourne l'id du génome et la fitness calculée

def eval_genomes(genomes, config):
    futures = []
    with ProcessPoolExecutor() as executor:
        for genome_id, genome in genomes:
            futures.append(executor.submit(evaluate_single_genome, genome_id, genome, config))

        for future in futures:
            genome_id, fitness = future.result()  # récupère les résultats du thread
            # Met à jour la fitness directement dans l'objet du génome correspondant
            next(g for g_id, g in genomes if g_id == genome_id).fitness = fitness
        
def run_neat(config, generation, checkpoint_name = None):
    
    if checkpoint_name != None:
        p = neat.Checkpointer.restore_checkpoint(str(checkpoint_name))
    else:
        p = neat.Population(config)
    
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    
    # Sauvegarde un checkpoint à chaque génération
    checkpointer = neat.Checkpointer(generation_interval=10, filename_prefix="NEAT_checkpoint\\neat-checkpoint-")
    p.add_reporter(checkpointer)

    winner = p.run(eval_genomes, generation)
    with open("Output_Data\\winner.pkl", "wb") as f:
        pickle.dump(winner, f)
# ----------------------------------------------------------

# Neat Start -----------------------------------------------
if __name__ == "__main__":
    # Neat Configuration -----------------------------------
    config_path = 'Input_Data\\Neat-config'
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                            neat.DefaultSpeciesSet, neat.DefaultStagnation,
                            config_path)
    # ------------------------------------------------------

    run_neat(config, 1000)
# ----------------------------------------------------------