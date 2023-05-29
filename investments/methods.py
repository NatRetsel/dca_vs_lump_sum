import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdate


class investment:
    def __init__(self, amount, hist_data) -> None:
        self.balance = amount
        self.hist_data = hist_data.copy(deep=True)
        self.avg_cost = 0
        self.unrealized_pnl = 0
        self.units = 0
        
    
class DCA(investment):
    def __init__(self, amount, hist_data, interval, lot_size=1) -> None:
        super().__init__(amount, hist_data)
        self.interval = interval
        self.lot_size = lot_size
    
    
    def simulate(self):
        cols = self.hist_data.columns.tolist() + ["Balance", "Shares", "Avg_cost", "Unrealized PnL"]
        self.hist_data = self.hist_data.reindex(columns = cols)
        for i in range(0, len(self.hist_data)):
            if i == 0 or i%self.interval == 0:
                # Buy if balance permits
                if self.balance > 0:
                    if self.balance >= self.hist_data['Open'].loc[i] * self.lot_size:
                        self.balance -= self.hist_data['Open'].loc[i] * self.lot_size
                        shares_bought = self.lot_size
                    else:
                        shares_bought = round(self.balance /self.hist_data['Open'].loc[i], 4)
                        self.balance = 0
                    self.avg_cost = ((self.avg_cost * self.units) + self.hist_data['Open'].loc[i] * shares_bought) / (self.units + shares_bought)
                    self.units += shares_bought
            self.unrealized_pnl = (self.hist_data['Close'].loc[i] - self.avg_cost) * self.units
            self.hist_data["Balance"].loc[i] = self.balance
            self.hist_data["Shares"].loc[i] = self.units
            self.hist_data["Avg_cost"].loc[i] = self.avg_cost
            self.hist_data["Unrealized PnL"].loc[i] = self.unrealized_pnl
            
    
    def plot_pnl(self):
        self.hist_data["Date"] = pd.to_datetime(self.hist_data["Date"], format="%Y-%m-%d")
        ax = sns.lineplot(data=self.hist_data, x=self.hist_data["Date"], y=self.hist_data["Unrealized PnL"])
        ax.xaxis.set_major_locator(mdate.YearLocator(5))
        ax.xaxis.set_major_formatter(mdate.DateFormatter("%Y"))
        plt.savefig("DCA.png", dpi=600)
                
                
                