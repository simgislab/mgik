#1 - reference (uikgeo)
#2 - being compared (mgik)

library(foreign)

wd = "d:\\Programming\\Python\\uik_geo\\mgik_uiks_comparison\\"
f_uik1_name = "moscow_uikgeo_20130826.dbf"
f_uik2_name = "moscow_mgik_w_coords.dbf"
f_out_name = "distances.csv"

#load data
d_uik1 = read.dbf(paste(wd,f_uik1_name,sep=""))
#d_uik1 = d_uik1[order(as.numeric(as.character(d_uik1$number_off))),]
d_uik2 = read.dbf(paste(wd,f_uik2_name,sep=""))

numrec = dim(d_uik1)[1]

res = c()
for (i in 1:numrec) {
    uik1 = subset(d_uik1,d_uik1$number_off == as.character(i))
    uik2 = subset(d_uik2,d_uik2$ID == i)
    
    if (dim(uik2)[1] != 0) {
        y1 = uik1$YCOORD
        x1 = uik1$XCOORD
        
        y2 = uik2$YCOORD
        x2 = uik2$XCOORD
        
        d = sqrt((y2 - y1)^2 + (x2 - x1)^2)
        res = rbind(res,c(i,d))
    }
}
res = data.frame(res)
names(res) <- c("ID","DISTANCE")
write.csv(res,paste(wd,f_out_name,sep=""),row.names=F)