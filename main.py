import pandas as pd
from investments.methods import DCA, lumpSum
pd.options.mode.chained_assignment = None 


if __name__ == '__main__':
    hist_data = pd.read_csv("Data/SPY_from_jan_1994.csv", header=[0])
    print(hist_data['Date'].iloc[0],type(hist_data['Date'].iloc[0]))
    print(hist_data['Date'].iloc[0].split('-')[0])
    # dca_1m = DCA(1000000, hist_data, 30,'fractional', 100)
    # dca_1m.simulate()
    # dca_1m.plot_pnl()
    # lump_sum_1m = lumpSum(1000000, hist_data, 'fractional')
    # lump_sum_1m.simulate()
    # lump_sum_1m.plot_pnl()
    # print(dca_1m.hist_data.head())
    # print(lump_sum_1m.hist_data.head())