# boxplot

d1 <- read.csv('/Users/tunder/Dropbox/python/character/dataforR/decade_optimums.tsv', sep = '\t')
d1$decade <- d1$decade + 5
d2 <- read.csv('/Users/tunder/Dropbox/python/character/dataforR/authgender_prediction_optimums.tsv', sep = '\t')
d2$decade <- d2$decade + 10
d1$predtype = 'character'
d2$predtype = 'author'
d3 <- rbind(d1, d2)
library(ggplot2)
library(scales)

p <- ggplot(d3, aes(x = decade, y = accuracy, fill = predtype, shape = predtype)) + 
  geom_point(alpha = 0.6, size = 2.5, color = 'black') +
  theme(text = element_text(size = 13)) +
  theme(plot.title = element_text(hjust = 0.5)) +
  scale_fill_manual('role\npredicted\n', values = c('green', 'blue')) +
  scale_shape_manual('role\npredicted\n', values = c(22, 23)) +
  scale_y_continuous('predictive accuracy\n', labels = percent, breaks = c(.55, .60, .65, .70, .75)) +
  xlab('') + ggtitle('Comparison of models predicting character gender\nto those that predict author gender\n')
plot(p)
        