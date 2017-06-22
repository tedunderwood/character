library(ggplot2)
library(scales)
library(dplyr)

best <- read.csv('/Users/tunder/Dropbox/python/character/charbyyearandauthgender.csv')
best$date <- as.numeric(as.character(best$date))
best$total <- as.numeric(as.character(best$total))
best<-arrange(best, date)
boysbymen = c()
girlsbymen = c()
boysbywomen = c()
girlsbywomen = c()
unknownchar = c()
unknownauth = c()

bm = filter(best, authgender == 'm', chargender == 'm')
gm = filter(best, authgender == 'm', chargender == 'f')
bw = filter(best, authgender == 'f', chargender == 'm')
gw = filter(best, authgender == 'f', chargender == 'f')
unchar = filter(best, chargender == 'u')
unauth = filter(best, authgender == 'u', chargender != 'u')

bm$total <- as.numeric(as.character(bm$total))
gm$total <- as.numeric(as.character(gm$total))
bw$total <- as.numeric(as.character(bw$total))
gw$total <- as.numeric(as.character(gw$total))

for (i in seq(1800, 2008, 2)) {
  thisbm = sum(bm$total[bm$date == i]) + sum(bm$total[bm$date == i+1])
  thisgm = sum(gm$total[gm$date == i]) + sum(gm$total[gm$date == i+1])
  thisbw =  sum(bw$total[bw$date == i]) + sum(bw$total[bw$date == i+1])
  thisgw = sum(gw$total[gw$date == i]) + sum(gw$total[gw$date == i+1])
  thisuc = sum(unchar$total[unchar$date == i]) + sum(unchar$total[unchar$date == i+1])
  thisua = sum(unauth$total[unauth$date == i]) + sum(unauth$total[unauth$date == i+1])
  total = thisbm + thisgm +thisbw + thisgw + thisuc + thisua
  
  boysbymen = c(boysbymen, thisbm/total)
  girlsbymen = c(girlsbymen, thisgm/total)
  boysbywomen = c(boysbywomen,thisbw/total)
  girlsbywomen = c(girlsbywomen, thisgw/total)
  unknownchar = c(unknownchar, thisuc/total)
  unknownauth = c(unknownauth, thisua/total)
}

df = data.frame(date = rep(seq(1800, 2008, 2), 6), 
                percentage = c(boysbymen, boysbywomen, girlsbywomen, girlsbymen, unknownauth, unknownchar),
                category = c(rep('words about men\nwritten by men\n', 105), rep('words about men\nwritten by women\n', 105),
                            rep('words about women\nwritten by women\n', 105), rep('words about women\nwritten by men\n', 105),
                            rep('authgender NA\n', 105), rep('chargender NA\n', 105)) )
df$category <- factor(df$category, levels = c('words about men\nwritten by men\n', 'words about men\nwritten by women\n',
                      'words about women\nwritten by women\n', 'words about women\nwritten by men\n',
                      'authgender NA\n', 'chargender NA\n'))
chromatic <- c("mediumorchid4", "mediumorchid1", "cadetblue1", 'cadetblue4', 'gray85', 'gray45')
theme_set(theme_gray(base_size=16))
p <- ggplot(df, aes(x=date, y=percentage, group = category, colour = category)) +
  scale_colour_manual('category\n', values = chromatic) +
  geom_area(aes(colour = category, fill = category), position = 'stack') + 
  scale_fill_manual("category\n", values = alpha(chromatic, 0.7)) +
  scale_x_continuous("") + scale_y_continuous("words as a percentage of the total", labels=percent) + 
  theme(axis.text = element_text(size=16))
print(p)
