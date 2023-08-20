import pandas as pd
from investments.methods import DCA
pd.options.mode.chained_assignment = None 


if __name__ == '__main__':
    hist_data = pd.read_csv("Data/SPY (1).csv", header=[0])
    dca_10k = DCA(1000000, hist_data, 30,'fractional', 100)
    dca_10k.simulate()
    dca_10k.plot_pnl()
    