library(ggplot2)
library(scales)
library(dplyr)

hathi <- read.csv('/Users/tunder/Dropbox/python/character/genre_experiment/post22_by_genre.csv')
nogenre <- filter(hathi, genre == 'none')
best <- arrange(nogenre, date)

bm = filter(best, authgender == 'm', chargender == 'm', date < 2010, date > 1799)
gm = filter(best, authgender == 'm', chargender == 'f', date < 2010, date > 1799)
bw = filter(best, authgender == 'f', chargender == 'm', date < 2010, date > 1799)
gw = filter(best, authgender == 'f', chargender == 'f', date < 2010, date > 1799)
bu = filter(best, authgender == 'u', chargender == 'm', date < 2010, date > 1799)
gu = filter(best, authgender == 'u', chargender == 'f', date < 2010, date > 1799)
nogenredates <- gw$date
nogenre = rep('unknown', length(nogenredates))
nogenreratio <- (gw$total + gm$total + gu$total) / (gw$total + bw$total + gm$total + bm$total + bu$total + gu$total)

hasgenre <- filter(hathi, genre != 'none')
best <- arrange(hasgenre, date)

bm = filter(best, authgender == 'm', chargender == 'm', date < 2010, date > 1799)
gm = filter(best, authgender == 'm', chargender == 'f', date < 2010, date > 1799)
bw = filter(best, authgender == 'f', chargender == 'm', date < 2010, date > 1799)
gw = filter(best, authgender == 'f', chargender == 'f', date < 2010, date > 1799)
bu = filter(best, authgender == 'u', chargender == 'm', date < 2010, date > 1799)
gu = filter(best, authgender == 'u', chargender == 'f', date < 2010, date > 1799)
hasgenredates <- gw$date

hasgenreratio <- (gw$total + gm$total + gu$total) / (gw$total + bw$total + gm$total + bm$total + bu$total + gu$total)
hasgenre = rep('genre', length(hasgenredates))
df <- data.frame(date = c(nogenredates, hasgenredates), 
                 womenratio = c(nogenreratio, hasgenreratio),
                 genre = c(nogenre, hasgenre))
p <- ggplot(df, aes(x = date, y = womenratio, color = genre)) + 
  geom_point() + geom_smooth(span = 0.4) + scale_x_continuous("") + 
  theme(text = element_text(size = 20)) +
  scale_y_continuous("", labels=percent, limits = c(0, 0.6)) +
  ggtitle('Description of women, as a percentage\nof characterization in fiction\n')
plot(p)