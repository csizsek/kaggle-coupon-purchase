import collections
import json
import pickle
import numpy as np
import pandas as pd
from pandas import DataFrame, Series
import traceback

us = pd.read_csv('data/user_list.csv')
cls = pd.read_csv('data/coupon_list_train_translated.csv')
cvs = pd.read_csv('data/coupon_visit_train.csv')
cds = pd.read_csv('data/coupon_detail_train.csv')
cas = pd.read_csv('data/coupon_area_train.csv')
ls = pd.read_csv('data/prefecture_locations.csv')

def prate_to_cat(prate):
    if prate < 50:
        return 'low'
    elif prate < 60:
        return 'medium'
    else:
        return 'high'
    
def cprice_to_cat(cprice):
    if cprice < 4480:
        return 'low'
    elif cprice < 10500:
        return 'medium'
    else:
        return 'high'

def dprice_to_cat(dprice):
    if dprice < 1980:
        return 'low'
    elif dprice < 3880:
        return 'medium'
    else:
        return 'high'

def gather_user_preferences():
    ups = {}
    for i in us.index[:]:
        u = us.ix[i]
        uh = u.USER_ID_hash
        ups[uh] = {
            'view_cnt': 0,
            'buy_cnt': 0,
            'capsule_text_view_cnt': collections.defaultdict(int),
            'capsule_text_buy_cnt': collections.defaultdict(int),
            'genre_view_cnt': collections.defaultdict(int),
            'genre_buy_cnt': collections.defaultdict(int),
            'large_area_view_cnt': collections.defaultdict(int),
            'large_area_buy_cnt': collections.defaultdict(int),
            'ken_view_cnt': collections.defaultdict(int),
            'ken_buy_cnt': collections.defaultdict(int),
            'small_area_view_cnt': collections.defaultdict(int),
            'small_area_buy_cnt': collections.defaultdict(int),
            'prate_view_cnt': collections.defaultdict(int),
            'prate_buy_cnt': collections.defaultdict(int),
            'cprice_view_cnt': collections.defaultdict(int),
            'cprice_buy_cnt': collections.defaultdict(int),
            'dprice_view_cnt': collections.defaultdict(int),
            'dprice_buy_cnt': collections.defaultdict(int)
        }
    exception_count = 0
    for j in cvs.index[:]:
        if j % 10000 == 0:
            print j
        cv = cvs.ix[j]
        uh = cv.USER_ID_hash
        ch = cv.VIEW_COUPON_ID_hash
        try:
            c = cls[cls.COUPON_ID_hash == cv.VIEW_COUPON_ID_hash].head(1)
            capsule_text = c.CAPSULE_TEXT.tolist()[0]
            genre = c.GENRE_NAME.tolist()[0]
            large_area = c.large_area_name.tolist()[0]
            ken = c.ken_name.tolist()[0]
            small_area = c.small_area_name.tolist()[0]
            prate = prate_to_cat(c.PRICE_RATE.tolist()[0])
            cprice = cprice_to_cat(c.CATALOG_PRICE.tolist()[0])
            dprice = dprice_to_cat(c.DISCOUNT_PRICE.tolist()[0])
            
            if cv.PURCHASE_FLG == 1:
                ups[uh]['buy_cnt'] += 1
                ups[uh]['capsule_text_buy_cnt'][capsule_text] += 1
                ups[uh]['genre_buy_cnt'][genre] += 1
                ups[uh]['large_area_buy_cnt'][large_area] += 1
                ups[uh]['ken_buy_cnt'][ken] += 1
                ups[uh]['small_area_buy_cnt'][small_area] += 1
                ups[uh]['prate_buy_cnt'][prate] += 1
                ups[uh]['cprice_buy_cnt'][cprice] += 1
                ups[uh]['dprice_buy_cnt'][dprice] += 1
            else:
                ups[uh]['view_cnt'] += 1
                ups[uh]['capsule_text_view_cnt'][capsule_text] += 1
                ups[uh]['genre_view_cnt'][genre] += 1
                ups[uh]['large_area_view_cnt'][large_area] += 1
                ups[uh]['ken_view_cnt'][ken] += 1
                ups[uh]['small_area_view_cnt'][small_area] += 1
                ups[uh]['prate_view_cnt'][prate] += 1
                ups[uh]['cprice_view_cnt'][cprice] += 1
                ups[uh]['dprice_view_cnt'][dprice] += 1
        except Exception as e:
            exception_count += 1
    print "exception count: {0}".format(exception_count)
    return ups

ups = gather_user_preferences()
print len(ups)
output = open('ups.pkl', 'wb')
pickle.dump(ups, output)
output.close()

