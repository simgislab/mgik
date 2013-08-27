wd = "d:\\Programming\\Python\\mgik\\"
f_uik_name = "mgik_uiks_all_20130827.csv"
f_out_name = "stats.csv"

#load data
d_uik = read.csv(paste(wd,f_uik_name,sep=""))

res = c()
num_rec = dim(d_uik)[1]
res = rbind(res,c("Всего УИКов",num_rec))

num_no_wkt = dim(subset(d_uik,d_uik$WKT == ""))[1]
res = rbind(res,c("Без координат места голосования",num_no_wkt))

num_no_wkt_o = dim(subset(d_uik,d_uik$WKT_O == ""))[1]
res = rbind(res,c("Без координат комиссии",num_no_wkt_o))

num_no_phone_v = dim(subset(d_uik,d_uik$PHONE_V == "none"))[1]
res = rbind(res,c("Без телефона места голосования",num_no_phone_v))

num_no_phone_o = dim(subset(d_uik,d_uik$PHONE_O == "none"))[1]
res = rbind(res,c("Без телефона комиссии",num_no_phone_o))

num_no_place_v = dim(subset(d_uik,d_uik$PLACE_V == "none"))[1]
res = rbind(res,c("Без места голосования",num_no_place_v))

num_no_place_o = dim(subset(d_uik,d_uik$PLACE_O == "none"))[1]
res = rbind(res,c("Без места комиссии",num_no_place_o))

res = data.frame(res)
names(res) <- c("STAT","VALUE")
write.csv(res,paste(wd,f_out_name,sep=""),row.names=F)