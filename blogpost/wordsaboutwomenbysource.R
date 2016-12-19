library(ggplot2)
library(scales)
library(dplyr)

hathi <- read.csv('/Users/tunder/Dropbox/python/character/corrected_hathi_summaries.csv')
best <- arrange(hathi, date)

bm = filter(best, authgender == 'm', chargender == 'm', date < 2010)
gm = filter(best, authgender == 'm', chargender == 'f', date < 2010)
bw = filter(best, authgender == 'f', chargender == 'm', date < 2010)
gw = filter(best, authgender == 'f', chargender == 'f', date < 2010)
hathidates <- gw$date

hathiratio <- (gw$total + gm$total) / (gw$total + bw$total + gm$total + bm$total)

chicago <-read.csv('/Users/tunder/Dropbox/python/character/chicago/chicago_summary.csv')

chic <- arrange(chicago, date)

bm = filter(chic, authgender == 'm', chargender == 'm')
gm = filter(chic, authgender == 'm', chargender == 'f')
bw = filter(chic, authgender == 'f', chargender == 'm')
gw = filter(chic, authgender == 'f', chargender == 'f')
chidates <- gm$date

chicagoratio <- (gw$total + gm$total) / (gw$total + bw$total + gm$total + bm$total)

df <- data.frame(date = c(hathidates, chidates), 
                 womenratio = c(hathiratio, chicagoratio), 
                 source = as.factor(c(rep('Hathi', length(hathidates)), rep('Chicago', length(chidates)))) )
p <- ggplot(df, aes(x = date, y = womenratio, color = source)) + 
  geom_point(aes(color = source)) + scale_x_continuous("") + 
  scale_colour_manual(values = c('red2', 'gray30')) + theme(text = element_text(size = 20)) +
  scale_y_continuous("", labels=percent, limits = c(0, 0.6)) +
  ggtitle('Description of women, as a percentage\nof characterization in fiction\n')
plot(p)