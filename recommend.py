import numpy as np
import pandas as pd
from pandas import DataFrame, Series
import collections
import json
import pickle
import datetime

counter = 0
ups = pickle.load(open('tmp/ups.pkl'))
clt = pd.read_csv('data/coupon_list_test_translated.csv')

def score(uh, ch):
    u = ups[uh]
    c = clt[clt.COUPON_ID_hash == ch].head(1)
    s = 0
    
    # genre
    genre = c.GENRE_NAME.tolist()[0]
    genre_view_score = u['genre_view_cnt'][genre]
    genre_buy_score = u['genre_buy_cnt'][genre]
    
    # large area
    large_area = c.large_area_name.tolist()[0]
    large_area_view_score = u['large_area_view_cnt'][genre]
    large_area_buy_score = u['large_area_buy_cnt'][genre]
    
    # ken
    ken = c.ken_name.tolist()[0]
    ken_view_score = u['ken_view_cnt'][genre]
    ken_buy_score = u['ken_buy_cnt'][genre]
    
    small_area = c.small_area_name.tolist()[0]
    small_area_view_score = u['small_area_view_cnt'][genre]
    small_area_buy_score = u['small_area_buy_cnt'][genre]
    
    GENRE_VIEW_WEIGHT = 1.61
    GENRE_BUY_WEIGHT = 2.61
    LARGE_AREA_VIEW_WEIGHT = 0.21
    LARGE_AREA_BUY_WEIGHT = 0.41
    KEN_VIEW_WEIGHT = 0.405
    KEN_BUY_WEIGHT = 0.63
    SMALL_AREA_VIEW_WEIGHT = 0.621
    SMALL_AREA_BUY_WEIGHT = 1.25
    
    s = (
        genre_view_score * GENRE_VIEW_WEIGHT +
        genre_buy_score * GENRE_BUY_WEIGHT +
        large_area_view_score * LARGE_AREA_VIEW_WEIGHT +
        large_area_buy_score * LARGE_AREA_BUY_WEIGHT +
        ken_view_score * KEN_VIEW_WEIGHT +
        ken_buy_score * KEN_BUY_WEIGHT +
        small_area_view_score * SMALL_AREA_VIEW_WEIGHT +
        small_area_buy_score * SMALL_AREA_BUY_WEIGHT
        )
    return s

def recommended_coupons(uh):
    global counter
    if counter % 100 == 0:
        print datetime.datetime.now(), counter
    counter += 1
    cs = clt
    cs['SCORE'] = cs.COUPON_ID_hash.apply(lambda ch: score(uh, ch))
    cs = cs.sort(columns=['SCORE', 'CATALOG_PRICE'], ascending=False)
    return " ".join(cs.COUPON_ID_hash[:5].tolist())

s = pd.read_csv('data/sample_submission.csv')
#s = s[:201]
s.PURCHASED_COUPONS = s.USER_ID_hash.apply(lambda uh: recommended_coupons(uh))

s.to_csv('submission/submit3.csv', index=False)

