# Import ---------------------------------------------------
import neat
from Simulation import Simulation
import pickle
# ----------------------------------------------------------

# Charger le gagnant
with open("Output_Data\\winner.pkl", "rb") as f:
    winner = pickle.load(f)
print(winner)

# Créer un réseau à partir du génome
config_path = 'Input_Data\\Neat-config'
config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                        neat.DefaultSpeciesSet, neat.DefaultStagnation,
                        config_path)

net = neat.nn.FeedForwardNetwork.create(winner, config)
sim = Simulation(sim_id=1, nn=net, init_money=10000, path_hist_data='Input_Data\\DF_ETHUSDT_15m.csv')
sim.start()
sim.export_sim_data()
