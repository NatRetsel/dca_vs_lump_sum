import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdate
import statistics
import numpy as np


class investment:
    def __init__(self, amount, hist_data) -> None:
        self.balance = amount
        self.hist_data = hist_data.copy(deep=True)
        self.avg_cost = 0
        self.unrealized_pnl = 0
        self.units = 0
        self.max_drawdown = None
        
        


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
        
    def calculate_metrics(self):
        market_monthly_returns = []
        market_daily_returns = []
        market_annual_returns = []
        
        port_monthly_returns = []
        port_daily_returns = []
        port_annual_returns = []
        
        # Calculate market return for a given time period
        # indexed dividend for that time period is added to the closing value for that period. 
        # This number is divided by closing valude at the beginning of time period
        # indexed dividend = total daily dividends / latest index divisor
        # divisor = market cap / value
        # note on close vs adj close. adj close is after paying dividends
            
        # annual and monthly market return
        curr_year = self.hist_data['Date'].iloc[0].split('-')[0]
        curr_month = self.hist_data['Date'].iloc[0].split('-')[1]
        year_open = 0
        year_closed = 0
        month_open = 0
        month_closed = 0
        for i in range(len(self.hist_data)):
            year = self.hist_data['Date'].iloc[i].split('-')[0]
            month = self.hist_data['Date'].iloc[i].split('-')[1]
            if i == 0:
                year_open = self.hist_data['Open'].iloc[i]
            if int(year) > curr_year:
                year_closed = self.hist_data['Close'].iloc[i-1]
                market_annual_returns.append((year_closed-year_open)/year_open)
                curr_year = int(year)
                year_open = self.hist_data['Open'].iloc[i]
            if int(month) != curr_month:
                month_closed = self.hist_data['Close'].iloc[i-1]
                market_monthly_returns.append((month_closed - month_open)/month_open)
                curr_month = int(month)
                month_open = self.hist_data['Open'].iloc[i]
            
        # annual and monthly portfolio return    
        curr_year = self.hist_data['Date'].iloc[0].split('-')[0]
        curr_month = self.hist_data['Date'].iloc[0].split('-')[1]
        year_open = 0
        year_closed = 0
        month_open = 0
        month_closed = 0
        for i in range(len(self.hist_data)):
            year = self.hist_data['Date'].iloc[i].split('-')[0]
            month = self.hist_data['Date'].iloc[i].split('-')[1]
            if i == 0:
                year_open = self.hist_data['Shares'].iloc[i] * self.hist_data['Avg_cost'].iloc[i]
            if int(year) > curr_year:
                year_closed = self.hist_data['Shares'].iloc[i-1] * self.hist_data['Avg_cost'].iloc[i-1]
                port_annual_returns.append((year_closed-year_open)/year_open)
                curr_year = int(year)
                year_open = self.hist_data['Shares'].iloc[i] * self.hist_data['Avg_cost'].iloc[i]
            if int(month) != curr_month:
                month_closed = self.hist_data['Shares'].iloc[i-1] * self.hist_data['Avg_cost'].iloc[i-1]
                port_monthly_returns.append((month_closed - month_open)/month_open)
                curr_month = int(month)
                month_open = self.hist_data['Shares'].iloc[i] * self.hist_data['Avg_cost'].iloc[i]
        
        # calc stdev of returns for portfolio and market
        #   - find mean returns over the period
        #   - square the difference between the return and the mean. e.g. (each month - mean)**2 or (each year - mean)**2
        #   - sum the squared difference / period - 1
        #   - square root it
        # alternatively, import statistics, statistics.stdev(sample)
        market_yearly_stdev = statistics.stdev(market_annual_returns)
        market_monthly_stdev = statistics.stdev(market_monthly_returns)
        port_yearly_stdev = statistics.stdev(port_annual_returns)
        port_monthly_stdev = statistics.stdev(port_monthly_returns)
        
        
        # Work out variance covariance matrix between portfolio and spy
        # np.cov(a,b)
        # statistics.variance(sample)
        annual_port_market_cov = np.cov(port_annual_returns, market_annual_returns)[0][1]
        monthly_port_market_cov = np.cov(port_monthly_returns, market_monthly_returns)[0][1]
        annual_market_var = statistics.variance(market_annual_returns)
        monthly_market_var = statistics.variance(market_monthly_returns)
        
        
        # Work out beta for portfolio
        # beta = np.cov(a,b)[0][1] / statistics.variance(sample)
        annual_beta = annual_port_market_cov/annual_market_var
        monthly_beta = monthly_port_market_cov/monthly_market_var
        
        # work out alpha (%) for portfolio 
        # assume risk free rate 5%
        # alpha = port return - risk free rate of return - beta(market return - risk free rate of return)
        annual_alpha = (self.hist_data["Unrealized PnL"].iloc[-1] - (self.hist_data["Shares"].iloc[0] * 
                                                                    self.hist_data["Avg_cost"].iloc[0] +
                                                                    self.hist_data["Balance"].iloc[0]))/((self.hist_data["Shares"].iloc[0] * 
                                                                    self.hist_data["Avg_cost"].iloc[0] +
                                                                    self.hist_data["Balance"].iloc[0])) - 0.05 - annual_beta*(((self.hist_data["Close"].iloc[-1] - 
                                                                                                                               self.hist_data["Open"].iloc[0])/self.hist_data["Open"].iloc[0])-0.05)
        
        monthly_alpha = (self.hist_data["Unrealized PnL"].iloc[-1] - (self.hist_data["Shares"].iloc[0] * 
                                                                    self.hist_data["Avg_cost"].iloc[0] +
                                                                    self.hist_data["Balance"].iloc[0]))/((self.hist_data["Shares"].iloc[0] * 
                                                                    self.hist_data["Avg_cost"].iloc[0] +
                                                                    self.hist_data["Balance"].iloc[0])) - 0.05 - monthly_beta*(((self.hist_data["Close"].iloc[-1] - 
                                                                                                                               self.hist_data["Open"].iloc[0])/self.hist_data["Open"].iloc[0])-0.05)
        
        # work out sharpe ratio
        # assume risk free rate 5%
        # SR = (port return - risk free rate)/stdev of portfolio excess return
        # stdev of portfolio excess return: stdev calculated earlier
        annual_sr = ((self.hist_data["Unrealized PnL"].iloc[-1] - (self.hist_data["Shares"].iloc[0] * 
                                                                    self.hist_data["Avg_cost"].iloc[0] +
                                                                    self.hist_data["Balance"].iloc[0]))/((self.hist_data["Shares"].iloc[0] * 
                                                                    self.hist_data["Avg_cost"].iloc[0] +
                                                                    self.hist_data["Balance"].iloc[0]))-0.05) / port_yearly_stdev
        
        monthly_sr = ((self.hist_data["Unrealized PnL"].iloc[-1] - (self.hist_data["Shares"].iloc[0] * 
                                                                    self.hist_data["Avg_cost"].iloc[0] +
                                                                    self.hist_data["Balance"].iloc[0]))/((self.hist_data["Shares"].iloc[0] * 
                                                                    self.hist_data["Avg_cost"].iloc[0] +
                                                                    self.hist_data["Balance"].iloc[0]))-0.05) / port_monthly_stdev
        
        # work out max drawdown
        #   - find minimum unrealized gain and look back for a peak. Compute difference
        
        pass
    
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
                
                
                