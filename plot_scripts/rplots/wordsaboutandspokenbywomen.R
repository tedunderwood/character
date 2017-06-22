library(ggplot2)
library(scales)
library(dplyr)

best <- read.csv('/Users/tunder/Dropbox/python/character/collated_summaries.csv')
best$date <- as.numeric(as.character(best$date))
best$total <- as.numeric(as.character(best$total))
best <- arrange(best, date)

bm = filter(best, authgender == 'm', chargender == 'm')
gm = filter(best, authgender == 'm', chargender == 'f')
bw = filter(best, authgender == 'f', chargender == 'm')
gw = filter(best, authgender == 'f', chargender == 'f')

girlratio <- (gw$total + gw$speaking) / (gw$total + bw$total + gw$speaking + bw$speaking)
boyratio <- (gm$total + gm$speaking) / (gm$total + bm$total + gm$speaking + bm$speaking)

df <- data.frame(date = rep(gm$date[gm$date > 1749 & gm$date < 2010], 2), 
                 womenratio = c(boyratio[bm$date > 1749 & bm$date < 2010], girlratio[gm$date > 1749 & gm$date < 2010]), 
                 authors = as.factor(c(rep('men', 260), rep('women', 260))) )
p <- ggplot(df, aes(x = date, y = womenratio, color = authors)) + 
  geom_point(aes(color = authors)) + scale_x_continuous("") + 
  scale_colour_manual(values = c('blue', 'red2')) +
  scale_y_continuous("words about women", labels=percent, limits = c(0, 0.6)) +
  ggtitle('Words about women, as a percentage\nof all characterization\n')
plot(p)