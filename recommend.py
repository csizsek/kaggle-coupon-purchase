import numpy as np
import pandas as pd
from pandas import DataFrame, Series
import collections
import json
import pickle
import datetime
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--ups')
parser.add_argument('--sub')

parser.add_argument('--buy')
#parser.add_argument('--view')

parser.add_argument('--capsule')
#parser.add_argument('--genre')

#parser.add_argument('--larea')
#parser.add_argument('--ken')
parser.add_argument('--sarea')

parser.add_argument('--prate')
parser.add_argument('--cprice')
#parser.add_argument('--dprice')
args = parser.parse_args()

ups_file_name = args.ups
#print ups_file_name
sub_file_name = args.sub
#print sub_file_name

BUY = float(args.buy)
#print BUY
#VIEW = float(args.view)
#print VIEW

CAPSULE = float(args.capsule)
#print CAPSULE
#GENRE = float(args.genre)
#print GENRE

#LAREA = float(args.larea)
#print LAREA
#KEN = float(args.ken)
#print KEN
SAREA = float(args.sarea)
#print SAREA

PRATE = float(args.prate)
#print PRATE
CPRICE = float(args.cprice)
#print CPRICE
#DPRICE = float(args.dprice)
#print DPRICE

VIEW = 0.1 * BUY

GENRE = 0.5 * CAPSULE

KEN = 0.4 * SAREA
LAREA = 0.1 * SAREA

DPRICE = 1.0 * CPRICE

ups_file = open(ups_file_name, 'rb')
ups = pickle.load(ups_file)
ups_file.close

clt = pd.read_csv('data/coupon_list_test_translated.csv')

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

def score(uh, ch):
    u = ups[uh]
    c = clt[clt.COUPON_ID_hash == ch].head(1)
    s = 0
    
    view_cnt = float(u['view_cnt'])
    if view_cnt == 0:
        view_cnt = 1000

    buy_cnt = float(u['buy_cnt'])
    if buy_cnt == 0:
        buy_cnt = 1000
    
    # capsule
    capsule = c.CAPSULE_TEXT.tolist()[0]
    capsule_view = u['capsule_text_view_cnt'][capsule]/view_cnt
    capsule_buy = u['capsule_text_buy_cnt'][capsule]/buy_cnt

    # genre
    genre = c.GENRE_NAME.tolist()[0]
    genre_view = u['genre_view_cnt'][genre]/view_cnt
    genre_buy = u['genre_buy_cnt'][genre]/buy_cnt
    
    # sarea
    sarea = c.small_area_name.tolist()[0]
    sarea_view = u['small_area_view_cnt'][sarea]/view_cnt
    sarea_buy = u['small_area_buy_cnt'][sarea]/buy_cnt
    
    # ken
    ken = c.ken_name.tolist()[0]
    ken_view = u['ken_view_cnt'][ken]/view_cnt
    ken_buy = u['ken_buy_cnt'][ken]/buy_cnt

    # larea
    larea = c.large_area_name.tolist()[0]
    larea_view = u['large_area_view_cnt'][larea]/view_cnt
    larea_buy = u['large_area_buy_cnt'][larea]/buy_cnt
    
    # prate
    prate = prate_to_cat(int(c.PRICE_RATE .tolist()[0]))
    prate_view = u['prate_view_cnt'][prate]/view_cnt
    prate_buy = u['prate_buy_cnt'][prate]/buy_cnt
    
    # cprice
    cprice = cprice_to_cat(int(c.CATALOG_PRICE.tolist()[0]))
    cprice_view = u['cprice_view_cnt'][cprice]/view_cnt
    cprice_buy = u['cprice_buy_cnt'][cprice]/buy_cnt

    # dprice
    dprice = dprice_to_cat(int(c.DISCOUNT_PRICE .tolist()[0]))
    dprice_view = u['dprice_buy_cnt'][dprice]/view_cnt
    dprice_buy = u['dprice_buy_cnt'][dprice]/buy_cnt
    
    s = (
        capsule_view * CAPSULE * VIEW +
        capsule_buy * CAPSULE * BUY +
        genre_view * GENRE * VIEW +
        genre_buy * GENRE * BUY +
        
        sarea_view * SAREA * VIEW +
        sarea_buy * SAREA * BUY +
        ken_view * KEN * VIEW +
        ken_buy * KEN * BUY +
        larea_view * LAREA * VIEW +
        larea_buy * LAREA * BUY +
        
        prate_view * PRATE * VIEW +
        prate_buy * PRATE * BUY +
        cprice_view * CPRICE * VIEW +
        cprice_buy * CPRICE * BUY +
        dprice_view * DPRICE * VIEW +
        dprice_buy * DPRICE * BUY
    )
    return s

import datetime
counter = 0

def recommended_coupons(uh):
    global counter
    if counter % 100 == 0:
        print datetime.datetime.now(), counter
    counter += 1
    cs = clt
    cs['SCORE'] = cs.COUPON_ID_hash.apply(lambda ch: score(uh, ch))
    sum_score = cs.SCORE.sum()
    cs = cs.sort(columns=['SCORE', 'CATALOG_PRICE'], ascending=False)
    #cs = cs[cs.SCORE > (sum_score * 0.005)]
    return " ".join(cs.COUPON_ID_hash[:3].tolist())

s = pd.read_csv('data/sample_submission.csv')
#s = s[:201]
s.PURCHASED_COUPONS = s.USER_ID_hash.apply(lambda uh: recommended_coupons(uh))

s.to_csv(sub_file_name, index=False)

