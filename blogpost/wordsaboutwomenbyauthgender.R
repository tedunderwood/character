library(ggplot2)
library(scales)
library(dplyr)

best <- read.csv('/Users/tunder/Dropbox/python/character/corrected_summaries.csv')
best$date <- as.numeric(as.character(best$date))
best$total <- as.numeric(as.character(best$total))
best <- arrange(best, date)

bm = filter(best, authgender == 'm', chargender == 'm')
gm = filter(best, authgender == 'm', chargender == 'f')
bw = filter(best, authgender == 'f', chargender == 'm')
gw = filter(best, authgender == 'f', chargender == 'f')

girlratio <- gw$total / (gw$total + bw$total)
boyratio <- gm$total / (gm$total + bm$total)

number = length(gm$date[gm$date > 1799 & gm$date < 2010])

df <- data.frame(date = rep(gm$date[gm$date > 1799 & gm$date < 2010], 2), 
                 womenratio = c(boyratio[bm$date > 1799 & bm$date < 2010], girlratio[gm$date > 1799 & gm$date < 2010]), 
                 authors = as.factor(c(rep('men', number), rep('women', number))) )
p <- ggplot(df, aes(x = date, y = womenratio, color = authors)) + 
  geom_point(aes(color = authors)) + scale_x_continuous("") + 
  scale_colour_manual(values = c('blue', 'red2')) + theme(text = element_text(size = 20)) +
  scale_y_continuous("words about women\n", labels=percent, limits = c(0, 0.6)) +
  ggtitle('Words about women, as a percentage\nof all characterization\n')
plot(p)