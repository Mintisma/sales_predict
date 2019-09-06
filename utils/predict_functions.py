def calc_ads(jitter_ads, list_score_weight, ads_spend, CPS):
    if ads_spend:
        X_ads = int(jitter_ads * list_score_weight * ads_spend / CPS)
    else:
        X_ads = 0

    return X_ads


def calc_coupon(jitter, list_score_weight, X_organic, coupon_rate):
    if coupon_rate:
        X_coupon = int(jitter * list_score_weight * X_organic * coupon_rate / 100)
    else:
        X_coupon = 0

    return X_coupon


def calc_deal(price, deal_price, deal_stock, jitter, X_organic, lightening_traffic_weight, lightening_time_weight):
    if deal_price:  # 如果做deal
        lightening_price = price - deal_price
        if lightening_price:
            lightening_price_weight = (price / lightening_price) ** 2
            X_lightening_order = int(jitter * X_organic * lightening_price_weight * lightening_traffic_weight * lightening_time_weight)
            if X_lightening_order > deal_stock:
                X_lightening_order = deal_stock
        else:
            X_lightening_order = 0
    else:
        X_lightening_order = 0

    return X_lightening_order