import math
import random
import sys

from utils.get_data import GetData
from utils.data_clean import Data_clean
from utils.predict_functions import calc_ads, calc_coupon, calc_deal


class Predict:
    def __init__(self, review_rate):
        self.week_ratio_dict = {1: 0.15, 2: 0.25, 3: 0.35, 4: 0.5, 5: 0.6, 6: 0.7, 7: 0.75, 8: 0.8, 9: 0.9, 10: 0.9,
                                11: 1, 12: 1.1, 13: 1.1, 14: 1.2, 15: 1.3, 16: 1.3, 17: 1.4, 18: 1.5, 19: 1.5, 20: 1.6,
                                21: 1.6, 22: 1.7, 23: 1.8, 24: 2}
        self.lightening_traffic_weight = 50
        self.lightening_time_weight = 1 / 28
        self.review_rate = review_rate
        self.marketing_base = 700
        self.if_out_stock = 0

    def predict_sales_week(self, avg_price, avg_order, keywords_sales, price, ads_spend, list_score, coupon_rate, stock,
                   deal_price=0, deal_stock=0, week_after_onshelf=1):
        # variable data type assuring
        price = float(price)
        ads_spend = float(ads_spend)  #广告花费
        list_score = float(list_score)  #listing得分
        coupon_rate = float(coupon_rate) #coupon
        stock = int(stock)  #库存
        deal_price = float(deal_price)  #降价
        deal_stock = int(deal_stock)   #秒杀库存上限
        week_after_onshelf = int(week_after_onshelf)   #上架第几周

        # variable derived
        price_weight = (price / avg_price) ** 5  #avg_price:类目平均价格
        if ads_spend > 1:
            CPS = math.log(ads_spend, 2) * math.log(price, 2) / 10 * price_weight
            if CPS == 0:
                CPS = 1
        else:
            CPS = 1
        list_score_weight = list_score * 1.3
        jitter = random.randrange(91, 110) / 100
        jitter_ads = random.randrange(70, 130) / 100

        # predict
        X_organic = int((jitter * list_score_weight * avg_order / price_weight * self.week_ratio_dict[week_after_onshelf]))#自然销量
        X_ads = calc_ads(jitter_ads, list_score_weight, ads_spend, CPS)#广告销量
        X_coupon = calc_coupon(jitter, list_score_weight, X_organic, coupon_rate)#coupon销量`
        #秒杀销量
        X_lightening_order = calc_deal(price, deal_price, deal_stock, jitter, X_organic, self.lightening_traffic_weight, self.lightening_time_weight)

        X_marketing = X_ads + X_coupon + X_lightening_order
        X_organic = int((1 + X_marketing / self.marketing_base) * X_organic)

        X_week = int(X_organic + X_marketing)
        if X_week==0:
            ratio_organic = 0
            ratio_ads = 0
            ratio_coupon = 0
            ratio_lightening_order = 0
        else:
            ratio_organic = X_organic / X_week
            ratio_ads = X_ads / X_week
            ratio_coupon = X_coupon / X_week
            ratio_lightening_order = X_lightening_order / X_week

        if X_week >= stock:
            self.if_out_stock = 1

            X_week = stock
            # X_organic = int(X_week * ratio_organic)
            X_ads = int(X_week * ratio_ads)
            X_coupon = int(X_week * ratio_coupon)
            X_lightening_order = int(X_week * ratio_lightening_order)
            # X_lightening_order = X_week - X_organic - X_ads - X_coupon
            X_organic = X_week - X_ads - X_coupon - X_lightening_order


        # result dict
        result_dict = {
            "salesresult": X_week,
            "Nature_sales": X_organic,
            "Ad_sales": X_ads,
            "coupon_sales": X_coupon,
            "seckilling_sales": X_lightening_order,
            "ifoutstock": self.if_out_stock,
            "reviewrate": self.review_rate,
            "sumsales": keywords_sales,
        }

        return result_dict


def main(keyword, review, stock, price, date_onshelf, list_score, ads_spend, deal_flag, coupon_rate=0, deal_price=0,
         deal_stock=0, week_after_onshelf=1, standard_listing_score=0.5,
         host='smads.cvj7a7mv2hkz.us-west-2.rds.amazonaws.com', user="sm_ppc", password="$Q3nBY6V0AByT6DW", dbname='sm_ad'):
    """
    param:
    1. keyword
    2. review: e.g. 1
    3. stock: e.g. 1000
    4. price: e.g. 5
    5. date_onshelf: e.g. 5
    6. list_score: (0, 1), 0 be the min list_score and 1 the max
    7. ad_spend : e.g. 10
    8. deal_flag: (1 or 0):
    9. coupon_rate: (0, 100), e.g. 5 means 95% percent of the original price
    10. deal_price: e.g. 3, which means -3 from original price
    11. deal_stock: e.g. 100, which means the total stock used for lightening deal
    12. week_after_onshelf: e.g. 5, which means 5 weeks after listing onshelf
    13. standard_listing_score: e.g. 0.3, 0.5, 0.8 for low, median and high competitiveness
    13. host: mysql connection
    14. user: mysql connection
    15. password: mysql connection
    16. dbname: mysql connection

    warning: coupon_rate, deal_price, deal_stock should be 0 if coupon, deal are not set.

    return: {
        "Nature_sales":25.759847304230426,  ## okay
        "salesresult":7025.759847304231,    ## okay
        "sumsales":1547400,
        "standard_sumsales": 15000,
        "Ad_sales":7000,    ## okay
        "ifoutstock":0,     ## okay
        "seckilling_sales":0,   ## okay
        "reviewrate":0.04902029210288225,   ##okay
        "coupon_sales":0    ## okay
        }
    """

    # get data from database
    gd = GetData(host=host, user=user, passwd=password, db=dbname)
    data = gd.get_data(keyword)

    # data clean
    cleaned_data = Data_clean(data)
    review_rate = cleaned_data.avg_rate

    # sales
    pd = Predict(review_rate)
    result_dict = pd.predict_sales_week(cleaned_data.avg_price, cleaned_data.avg_order, cleaned_data.total_sales, price,
                                    ads_spend, list_score, coupon_rate, stock, deal_price, deal_stock, week_after_onshelf)

    # get competitor sales
    jitter = random.randrange(90, 110) / 100
    standard_listing_score *= jitter
    standard_sumsales = pd.predict_sales_week(cleaned_data.avg_price, cleaned_data.avg_order, cleaned_data.total_sales, price,
                                    ads_spend, standard_listing_score, coupon_rate, stock, deal_price, deal_stock, week_after_onshelf)

    result_dict['standard_salesresult'] = standard_sumsales['salesresult']

    return result_dict


if __name__ == '__main__':
    keyword = sys.argv[1]
    review = int(sys.argv[2])
    stock = int(sys.argv[3])
    price = float(sys.argv[4])
    date_onshelf = int(sys.argv[5])
    listing_score = float(sys.argv[6])
    ads_spend = float(sys.argv[7])
    deal_flag=int(sys.argv[8])
    coupon_rate=int(sys.argv[9])
    deal_price=float(sys.argv[4])-float(sys.argv[10])
    deal_stock=int(sys.argv[11])
    week_after_onshelf=int(sys.argv[12])
    standard_listing_score = float(sys.argv[13])
    host=sys.argv[14]
    user=sys.argv[15]
    password=sys.argv[16]
    dbname=sys.argv[17]
    result_dict = main(keyword, review, stock, price, date_onshelf, listing_score, ads_spend, deal_flag, coupon_rate,
                       deal_price, deal_stock, week_after_onshelf, standard_listing_score, host, user, password, dbname)
    # print(result_dict)
    # result_dict = main("aaa batteries energizer", 10, 5000, 10.0, 1, 0.7, 1, 1, 20, 0, 300, 20, 1, 'edu.dev.sellermotor.com'
    #                        , 'smedu', 'wcw2iE2Txp3ZZAiy', 'sm_edu')
    # print(result_dict)
