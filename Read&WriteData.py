import numpy as np
import pandas as pd

def CSVtoNumpyArray(file_path):
    """Convertit un fichier CSV en tableau NumPy."""
    data = pd.read_csv(file_path)
    return data.to_numpy()

def NumpyArraytoCSV(array, file_path):
    """Convertit un tableau NumPy en fichier CSV."""
    df = pd.DataFrame(array)
    df.to_csv(file_path, index=False)

# Convertir un CSV en tableau NumPy
numpy_array = CSVtoNumpyArray('ETHUSDT_15m.csv')

new_numpy_array = numpy_array.copy()

for i, row in enumerate(numpy_array):
    new_numpy_array[i, 0] = row[0] #opentime
    new_numpy_array[i, 1] = 1 #open
    new_numpy_array[i, 2] = row[2]/row[1] #hight
    new_numpy_array[i, 3] = row[3]/row[1] #low
    new_numpy_array[i, 4] = row[4]/row[1] #close
    new_numpy_array[i, 5] = row[5] #volume
    new_numpy_array[i, 6] = row[6] #closetime

# NumpyArraytoCSV(new_numpy_array, 'DF_ETHUSDT_15m.csv')
    
