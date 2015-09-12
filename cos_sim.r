### Kaggle Scripts: Ponpare Coupon Purchase Prediction ###
### Author: Subhajit Mandal ###

#read in all the input data
cpdtr <- read.csv("data/coupon_detail_train.csv")
cpltr <- read.csv("data/coupon_list_train.csv")
cplte <- read.csv("data/coupon_list_test.csv")
ulist <- read.csv("data/user_list.csv")

#making of the train set
train <- merge(cpdtr,cpltr)
train <- train[,c("COUPON_ID_hash","USER_ID_hash",
                  "GENRE_NAME","DISCOUNT_PRICE","PRICE_RATE",
                  "USABLE_DATE_MON","USABLE_DATE_TUE","USABLE_DATE_WED","USABLE_DATE_THU",
                  "USABLE_DATE_FRI","USABLE_DATE_SAT","USABLE_DATE_SUN","USABLE_DATE_HOLIDAY",
                  "USABLE_DATE_BEFORE_HOLIDAY","large_area_name","ken_name","small_area_name")]
print("a")
print(dim(train))
print(head(train, 3))

#combine the test set with the train
cplte$USER_ID_hash <- "dummyuser"
cpchar <- cplte[,c("COUPON_ID_hash","USER_ID_hash",
                   "GENRE_NAME","DISCOUNT_PRICE","PRICE_RATE",
                   "USABLE_DATE_MON","USABLE_DATE_TUE","USABLE_DATE_WED","USABLE_DATE_THU",
                   "USABLE_DATE_FRI","USABLE_DATE_SAT","USABLE_DATE_SUN","USABLE_DATE_HOLIDAY",
                   "USABLE_DATE_BEFORE_HOLIDAY","large_area_name","ken_name","small_area_name")]
print("b")
print(dim(cpchar))
print(head(cpchar, 3))

train <- rbind(train,cpchar)
print("c")
print(dim(train))
print(head(train, 3))


#NA imputation
train[is.na(train)] <- 1

#feature engineering
train$DISCOUNT_PRICE <- 1/log10(train$DISCOUNT_PRICE)
train$PRICE_RATE <- (train$PRICE_RATE*train$PRICE_RATE)/(100*100)
print("d")
print(dim(train))
print(head(train, 3))


#convert the factors to columns of 0's and 1's
train <- cbind(train[,c(1,2)],model.matrix(~ -1 + .,train[,-c(1,2)],
                                                    contrasts.arg=lapply(train[,names(which(sapply(train[,-c(1,2)], is.factor)==TRUE))], contrasts, contrasts=FALSE)))
print("e")
print(dim(train))
print(head(train, 3))

#separate the test from train
test <- train[train$USER_ID_hash=="dummyuser",]
test <- test[,-2]
print("f")
print(dim(test))
print(head(test, 3))

train <- train[train$USER_ID_hash!="dummyuser",]
print("g")
print(dim(train))
print(head(train, 3))

#data frame of user characteristics
uchar <- aggregate(.~USER_ID_hash, data=train[,-1],FUN=mean)
uchar$DISCOUNT_PRICE <- 1
uchar$PRICE_RATE <- 1
print("h")
print(dim(uchar))
print(head(uchar, 3))

#Weight Matrix: GENRE_NAME DISCOUNT_PRICE PRICE_RATE USABLE_DATE_ large_area_name ken_name small_area_name
require(Matrix)
W <- as.matrix(Diagonal(x=c(rep(2.05,13), rep(2,1), rep(-0.13,1), rep(0,9), rep(0.5,9), rep(1.01,47), rep(4.75,55))))
print("i")
print(dim(W))
print(head(W, 3))

#calculation of cosine similairties of users and coupons
#score = as.matrix(uchar[,2:ncol(uchar)]) %*% W %*% t(as.matrix(test[,2:ncol(test)]))
r1 = as.matrix(uchar[,2:ncol(uchar)]) %*% W
print("j")
print(dim(r1))
print(head(r1, 3))

score = r1 %*% t(as.matrix(test[,2:ncol(test)]))
print("k")
print(dim(score))
print(head(score, 3))

#order the list of coupons according to similairties and take only first 10 coupons
uchar$PURCHASED_COUPONS <- do.call(rbind, lapply(1:nrow(uchar),FUN=function(i){
  purchased_cp <- paste(test$COUPON_ID_hash[order(score[i,], decreasing = TRUE)][1:10],collapse=" ")
  return(purchased_cp)
}))

#make submission
submission <- merge(ulist, uchar, all.x=TRUE)
submission <- submission[,c("USER_ID_hash","PURCHASED_COUPONS")]
write.csv(submission, file="submission/cosine_sim_r.csv", row.names=FALSE)

