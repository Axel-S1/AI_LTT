import numpy as np
import pandas as pd
from tqdm import tqdm    

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
        if   (self.value * (1+((data[3]-1) * self.leverage))) / self.initial_value <= self.SL:
            self.value = self.initial_value * self.SL
            self.close_cause = "SL"
            self.close_time = data[-1]
            return True
            
        elif (self.value * (1+((data[2]-1) * self.leverage))) / self.initial_value >= self.TP:
            self.value = self.initial_value * self.TP
            self.close_cause = "TP"
            self.close_time = data[-1]
            return True
            
        else:
            self.value = self.value * (1+((data[4]-1) * self.leverage))
            return False

class Simulation():
    def __init__(self, sim_id, init_money, nn, path_hist_data):
        
        self.ID = sim_id
        self.nn = nn
        self.path_hist_data = path_hist_data
        self.hist_data = self.__get_data()
        
        self.fees = 2e-4
        self.min_bid = 25
        self.len_frame = 96
        self.break_malus = 0
        self.initial_money = init_money
        self.money = init_money
        
        self.en_orders = []
        self.di_orders = []
        
        self.simulation_data = []
        self.simulation_orders = []
        self.fitness = 0
        
    def start(self):
        for i in range(len(self.hist_data)-self.len_frame-1):
            self.step(i)
            
            if self.simulation_data[-1]["all_money"] < self.initial_money*0.5:
                self.break_malus = 50000
                break
            
            elif i >= 15000 and self.simulation_data[-1]["nb_di_orders"] < 20:
                self.break_malus = 100000
                break
            
        self.__close_and_store_all_trades()
        self.__update_info(i)
        self.__fitness_score()
        return self.fitness
        
    def step(self, i):
        self.__update_info(i)
        
        step_data = (list(self.hist_data[i:i+self.len_frame , 1:5].flatten()))
        step_data = step_data + [self.simulation_data[-1]["wallet_money"], self.simulation_data[-1]["invest_money"], self.simulation_data[-1]["nb_en_orders"]]
        output = self.nn.activate(tuple(step_data))
             
        if output[0] > 0.5:
            self.__make_order(self.hist_data[i, 0], int(output[1]*10), self.money*output[2], output[3], output[4]) # temporaire
            
        for order in self.en_orders:
            if order.step(self.hist_data[i]):
                self.money += (order.value*(1-self.fees))
                self.di_orders.append(order)
                self.en_orders.remove(order)
        
    def export_sim_data(self):
        def NumpyArraytoCSV(array, file_path):
            df = pd.DataFrame(array)
            df.to_csv(file_path, index=False)
            
        NumpyArraytoCSV(self.simulation_data, f'Output_Data\\Simulation{self.ID}_main_data.csv')
        NumpyArraytoCSV(self.simulation_orders, f'Output_Data\\Simulation{self.ID}_trade_data.csv')
        
    def __get_data(self):
        data = pd.read_csv(self.path_hist_data).to_numpy()
        return data[-105192:,:]
            
    def __make_order(self, ref_opentime, ref_leverage, ref_value, ref_SL, ref_TP):
        if self.money >= ref_value and ref_value >= self.min_bid:
            self.money -= ref_value*(1+self.fees)
            self.en_orders.append(Order(ref_opentime, ref_leverage, ref_value, ref_SL, ref_TP))
    
    def __update_info(self, i):
        # Calcul des informations pour chaque étape
        invest_money = sum(order.value for order in self.en_orders)
        # Ajout des informations à l'historique
        info = {
            "timestamp" :   self.hist_data[i][0],
            "wallet_money": self.money, #
            "invest_money": invest_money, #
            "all_money" :   self.money + invest_money,
            "nb_en_orders": len(self.en_orders), #
            "nb_di_orders": len(self.di_orders),
        }
        self.simulation_data.append(info)
        
    def __close_and_store_all_trades(self):
        while len(self.en_orders) > 0:
            for order in self.en_orders:
                self.money += (order.value*(1-self.fees))
                order.close_time = self.hist_data[-1][-1]
                order.close_cause = "NONE"
                self.di_orders.append(order)
                self.en_orders.remove(order)
            
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
                    
    def __fitness_score(self):
        # Coef ----------------------
        coefs = [0.5, 1.25, 0.75]
        
        # Intermediate Calcul -------
        self.money_earn = self.simulation_data[-1]["all_money"] - self.initial_money
        day_gain = []
        for i in range(96, len(self.simulation_data), 96):
            day_gain.append(self.simulation_data[i]["all_money"] / self.simulation_data[i-96]["all_money"]) 
        
        if len(day_gain) > 0:
            self.max_drawdown = np.abs((np.min(day_gain)-1)*100)
        else:
            self.max_drawdown = 0

        
        # fitness value -------------        
        self.fitness += self.money_earn
        self.fitness += np.log1p(len(self.di_orders))*0.5
        self.fitness /= (self.max_drawdown + 1)
        
        self.fitness -= self.break_malus
