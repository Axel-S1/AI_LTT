# Import ---------------------------------------------------
import neat
from tqdm import tqdm
from Simulation import Simulation
from concurrent.futures import ProcessPoolExecutor, as_completed
# ----------------------------------------------------------


# Fonction -------------------------------------------------
def eval_genomes(genomes, config):
    for genome_id, genome in tqdm(genomes):
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        sim = Simulation(sim_id=genome_id, nn=net, init_money=10000, path_hist_data='Input_Data\\DF_ETHUSDT_15m.csv')
        genome.fitness = sim.start()
        
def run_neat(config,checkpoint_name = None):
    
    if checkpoint_name != None:
        p = neat.Checkpointer.restore_checkpoint(str(checkpoint_name))
    else:
        p = neat.Population(config)
    
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(200))

    winner = p.run(eval_genomes,10)
# ----------------------------------------------------------


# Neat Configuration ---------------------------------------
config_path = 'Neat-config'
config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                        neat.DefaultSpeciesSet, neat.DefaultStagnation,
                        config_path)
# ----------------------------------------------------------

# Neat Start -----------------------------------------------
run_neat(config)
# ----------------------------------------------------------