# boxplot

d2 <- read.csv('/Users/tunder/Dropbox/python/character/dataforR/decade_optimums.tsv', sep = '\t')
library(ggplot2)
library(scales)

p <- ggplot(d2, aes(x = decade, y = accuracy)) + 
  geom_point(color = 'black', alpha = 0.6, shape = 21, fill = 'blue2', size = 2) +
  theme(text = element_text(size = 14)) +
  theme(plot.title = element_text(hjust = 0.5)) +
  scale_y_continuous('predictive accuracy\n', labels = percent) +
  xlab('') + ggtitle('Accuracy of gender prediction, 1600-character samples\n')
plot(p)
        