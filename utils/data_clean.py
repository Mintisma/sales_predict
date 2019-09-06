import pandas as pd


def orders(data):
    sales, price = data
    order = int(float(sales) / float(price))
    return order


class Data_clean:
    def __init__(self, data):
        self.data = data
        self.df = self.data2dataframe()
        self.avg_price = self.mean_price()
        self.avg_order = self.mean_order()
        self.avg_sales = self.mean_sales()
        self.avg_rate = self.review_rate()
        self.total_sales = self.sum_sales()

    def data2dataframe(self):
        df = pd.DataFrame(self.data)
        df = df.dropna()
        df = df[(df.est_sales != '') & (df.est_sales != '0') & (df.price != '') & (df.price != '0') & (
                    df.reviews_30d != '')]
        df.price = df.price.astype('float')
        df.est_sales = df.est_sales.astype('float')
        df.reviews_30d = df.reviews_30d.astype('float')
        df = df[df.est_sales > 0]
        df['orders'] = df[['est_sales', 'price']].apply(orders, axis=1)
        return df

    def mean_price(self):
        avg_price = self.df['price'].mean()
        return avg_price

    def mean_order(self):
        avg_orders = self.df['orders'].mean()
        return avg_orders

    def mean_sales(self):
        avg_sales = self.df['est_sales'].mean()
        return avg_sales

    def review_rate(self):
        avg_rate = self.df['reviews_30d'].sum() / self.df['orders'].sum()
        return round(avg_rate, 3)

    def sum_sales(self):
        total_sales = self.df['est_sales'].sum()
        return total_sales
