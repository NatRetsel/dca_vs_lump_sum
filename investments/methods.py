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


class lumpSum(investment):
    def __init__(self, amount, hist_data, order_type="default") -> None:
        """Constructor for the lumpSum class

        Args:
            amount (int/float): Initial capital
            hist_data (pandas DataFrame): Historical market data for simulation
            order_type (str, optional): Determines if lump sum has to be whole shares
                                        when it is "default". If "fractional", lump sum will be based on cash amount
                                        Defaults to "default".
        """    
        super().__init__(amount, hist_data)
        self.order_type = order_type
    
    def simulate(self):
        """simulating Lump Sum process
            Iterates over the historical market data in steps specified with interval. Go long at open only when self.balance > 0
            - order_type == "default"
                - number of whole shares determined with amount // open price at time 0
            
            - order_type == "fractional"
                - Shares purchased will be fractional computed by dividing amount by cost of equity at open on day 0
        """
        cols = self.hist_data.columns.tolist() + ["Balance", "Shares", "Avg_cost", "Unrealized PnL"]
        self.hist_data = self.hist_data.reindex(columns = cols)
        shares_bought = 0
        
        # Buy if balance permits
        for i in range(0, len(self.hist_data)):
            if i == 0:
                if self.balance > 0:
                    if self.order_type == "default":
                        if self.balance >= self.hist_data['Open'].loc[0]:
                            shares_bought = self.balance //self.hist_data['Open'].loc[0]
                            self.balance -= self.hist_data['Open'].loc[0] * self.balance //self.hist_data['Open'].loc[0]
                    
                    elif self.order_type == "fractional":
                        shares_bought = self.balance/self.hist_data['Open'].loc[0]
                        self.balance = 0
                self.avg_cost = ((self.avg_cost * self.units) + self.hist_data['Open'].loc[0] * shares_bought) / (self.units + shares_bought)
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
        plt.savefig("lumpSum.png", dpi=600)
        plt.close('all')

    
class DCA(investment):
    def __init__(self, amount, hist_data, interval, order_type="default", lot_size=1) -> None:
        """Constructor for the DCA class

        Args:
            amount (int/float): Initial capital
            hist_data (pandas DataFrame): Historical market data for simulation
            interval (int): Days interval to DCA
            order_type (str, optional): Determines if DCA is based on number of shares specified in lot_size
                                        when it is "default". If "fractional", DCA will be based on cash amount
                                        specified in lot_size. Defaults to "default".
            lot_size (int, optional): number of shares if order_type is "default", cash amount if order_type is "fractional". Defaults to 1.
        """
        super().__init__(amount, hist_data)
        self.interval = interval
        self.lot_size = lot_size
        self.order_type = order_type
    
    
    def simulate(self) -> None:
        """simulating DCA process
            Iterates over the historical market data in steps specified with interval. Go long at open only when self.balance > 0
            - order_type == "default"
                - DCA amount of shares specified with lot_size.
                - If remaining balance is less than what could be purchased at lot_size, work out the max whole shares that could be purchased
            
            - order_type == "fractional"
                - DCA amount specified by lot_size.
                - Shares purchased will be fractional computed by dividing lot_size by cost of equity at open on day of DCA
        """
        cols = self.hist_data.columns.tolist() + ["Balance", "Shares", "Avg_cost", "Unrealized PnL"]
        self.hist_data = self.hist_data.reindex(columns = cols)
        shares_bought = 0
        for i in range(0, len(self.hist_data)):
            if i == 0 or i%self.interval == 0:
                # Buy if balance permits
                if self.balance > 0:
                    if self.order_type == "default":
                        if self.balance >= self.hist_data['Open'].loc[i] * self.lot_size:
                            self.balance -= self.hist_data['Open'].loc[i] * self.lot_size
                            shares_bought = self.lot_size
                        else:
                            shares_bought = self.balance //self.hist_data['Open'].loc[i]
                            self.balance = self.balance - (self.hist_data['Open'].loc[i] * shares_bought)
                    
                    elif self.order_type == "fractional":
                        if self.balance >= self.lot_size:
                            self.balance -= self.lot_size
                            shares_bought = self.hist_data['Open'].loc[i] / self.lot_size
                        else:
                            shares_bought = self.hist_data['Open'].loc[i] / self.balance
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
        plt.close('all')
                
                
                