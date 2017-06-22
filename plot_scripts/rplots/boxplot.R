# boxplot

d2 <- read.csv('/Users/tunder/Dropbox/python/character/authgenderpredict/decades.csv')
library(ggplot2)
library(scales)
#d2$floor[d2$model == 'authors'] <- d2$floor[d2$model == 'authors'] + 10
d2$grouper = as.factor(paste(d2$floor, d2$model))


p <- ggplot(d2, aes(x = as.integer(floor), y = accuracy, color = model, fill = model, group = grouper)) + 
  geom_boxplot(position = 'identity') +
  scale_color_manual(values = c('peachpuff4', 'palegreen4')) +
  scale_fill_manual(values = c('peachpuff1', 'palegreen1')) +
  theme(text = element_text(size = 18)) +
  scale_y_continuous('predictive accuracy\n', labels = percent, breaks = c(0.55, 0.6, 0.65, 0.7, 0.75)) +
  scale_x_continuous('') +
  ggtitle('Comparison of models that use character data\nto predict the gender of characters, or authors\n')
plot(p)
        