# boxplot

d2 <- read.csv('/Users/tunder/Dropbox/python/character/dataforR/decade_optimums.tsv', sep = '\t')
library(ggplot2)
library(scales)

p <- ggplot(d2, aes(x = decade, y = accuracy)) + 
  geom_point(color = 'blue2') +
  theme(text = element_text(size = 14)) +
  scale_y_continuous('predictive accuracy\n', labels = percent)
plot(p)
        