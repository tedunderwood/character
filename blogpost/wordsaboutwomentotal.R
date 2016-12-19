library(ggplot2)
library(scales)
library(dplyr)

hathi <- read.csv('/Users/tunder/Dropbox/python/character/corrected_hathi_summaries.csv')
best <- arrange(hathi, date)

bm = filter(best, authgender == 'm', chargender == 'm', date < 2010, date > 1799)
gm = filter(best, authgender == 'm', chargender == 'f', date < 2010, date > 1799)
bw = filter(best, authgender == 'f', chargender == 'm', date < 2010, date > 1799)
gw = filter(best, authgender == 'f', chargender == 'f', date < 2010, date > 1799)
bu = filter(best, authgender == 'u', chargender == 'm', date < 2010, date > 1799)
gu = filter(best, authgender == 'u', chargender == 'f', date < 2010, date > 1799)
hathidates <- gw$date

hathiratio <- (gw$total + gm$total + gu$total) / (gw$total + bw$total + gm$total + bm$total + bu$total + gu$total)

# chicago <-read.csv('/Users/tunder/Dropbox/python/character/chicago/chicago_summary.csv')
# 
# chic <- arrange(chicago, date)
# 
# bm = filter(chic, authgender == 'm', chargender == 'm')
# gm = filter(chic, authgender == 'm', chargender == 'f')
# bw = filter(chic, authgender == 'f', chargender == 'm')
# gw = filter(chic, authgender == 'f', chargender == 'f')
# chidates <- gm$date
# 
# chicagoratio <- (gw$total + gm$total) / (gw$total + bw$total + gm$total + bm$total)

df <- data.frame(date = hathidates, 
                 womenratio = hathiratio )
p <- ggplot(df, aes(x = date, y = womenratio)) + 
  geom_point() + geom_smooth(span = 0.4) + scale_x_continuous("") + 
  theme(text = element_text(size = 20)) +
  scale_y_continuous("", labels=percent, limits = c(0, 0.6)) +
  ggtitle('Description of women, as a percentage\nof characterization in fiction\n')
plot(p)