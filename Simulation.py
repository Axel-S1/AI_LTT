import numpy as np
import pandas as pd
import random as r
from tqdm import tqdm 

def CSVtoNumpyArray(file_path):
    """Convertit un fichier CSV en tableau NumPy."""
    data = pd.read_csv(file_path)
    return data.to_numpy()
def NumpyArraytoCSV(array, file_path):
    """Convertit un tableau NumPy en fichier CSV."""
    df = pd.DataFrame(array)
    df.to_csv(file_path, index=False)
FIRST_ORDER_INFO = ["long"]

class Order():
    def __init__(self, ref_opentime, ref_leverage, ref_value, ref_SL, ref_TP):
        self.opentime = ref_opentime
        
        self.initial_value = ref_value
        self.value = ref_value
        self.leverage = ref_leverage
        self.SL = ref_SL
        self.TP = ref_TP
        
        self.close_time = None
        self.close_cause = None
        
    def step(self, data):
        if (self.value * (data[3] * self.leverage)) / self.initial_value <= self.SL:
            self.value = self.initial_value * self.SL
            self.close_cause = "SL"
            self.close_time = data[-1]
            return True
            
        elif (self.value * (data[2] * self.leverage)) / self.initial_value >= self.TP:
            self.value = self.initial_value * self.TP
            self.close_cause = "TP"
            self.close_time = data[-1]
            return True
            
        else:
            self.value = self.value * (data[4] * self.leverage)
            return False

class Simulation():
    def __init__(self, ref_init_money, hist_data):
        self.en_orders = []
        self.di_orders = []
        self.money = ref_init_money
        self.hist_data = hist_data
        
        self.simulation_data = []
        self.simulation_orders = []
        self.fees = 2e-4
        self.min_bid = 0
    
    def step(self):
        # TODO : une IA qui choisira si elle veux faire un ordre (long ou rien).
        # Avec les params de levier, valeur de l'ordre et les "stop loss and take profit".
        if r.randint(0, 1000) == 3: # temporaire
            self.__make_order(self.hist_data[0][-1], 1, self.money*0.05, 0.8, 1.1) # temporaire
            self.temp = False
            
        for order in self.en_orders:
            if order.step(self.hist_data[0]):
                self.money += (order.value*(1-self.fees))
                self.di_orders.append(order)
                self.en_orders.remove(order)
                    
        self.__update_info()
        self.hist_data = self.hist_data[1:]
            
    def __make_order(self, ref_opentime, ref_leverage, ref_value, ref_SL, ref_TP):
        if self.money >= ref_value and ref_value >= self.min_bid:
            self.money -= ref_value*(1+self.fees)
            self.en_orders.append(Order(ref_opentime, ref_leverage, ref_value, ref_SL, ref_TP))
    
    def __update_info(self):
        # Calcul des informations pour chaque étape
        invest_money = sum(order.value for order in self.en_orders)
        nb_en_orders = len(self.en_orders)
        nb_di_orders = len(self.di_orders)
        # Ajout des informations à l'historique
        info = {
            "timestamp" : self.hist_data[0][0],
            "wallet_money": self.money,
            "invest_money": invest_money,
            "all_money" : self.money + invest_money,
            "nb_en_orders": nb_en_orders,
            "nb_di_orders": nb_di_orders,
            "nb_any_orders": nb_en_orders + nb_di_orders,
        }
        self.simulation_data.append(info)
        
    def send_all_trade(self):
        for order in self.di_orders:
            info = {
            "opentime": order.opentime,
            "initial_value": order.initial_value,
            "value" : order.value,
            "leverage": order.leverage,
            "SL": order.SL,
            "TP": order.TP,
            "close_time": order.close_time,
            "close_cause": order.close_cause,
            }
            self.simulation_orders.append(info)
            
        return self.simulation_orders
    
#  Main ------------------------------------------------------------------------
historical_data = CSVtoNumpyArray('DF_ETHUSDT_15m.csv')
sim1 = Simulation(10000, historical_data)

for i in tqdm(range(len(historical_data))):
    sim1.step()
       
NumpyArraytoCSV(sim1.simulation_data, 'sim_data.csv')
NumpyArraytoCSV(sim1.send_all_trade(), 'trade_data.csv')