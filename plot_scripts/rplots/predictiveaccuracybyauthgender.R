# boxplot

d2 <- read.csv('/Users/tunder/Dropbox/python/character/dataforR/auth_specific_optimums.tsv', sep = '\t')
library(ggplot2)
library(scales)

p <- ggplot(d2, aes(x = decade, y = accuracy, fill = authgender, shape = authgender)) + 
  geom_point(alpha = 0.66, size = 2.5, color = 'black') +
  theme(text = element_text(size = 13)) +
  theme(plot.title = element_text(hjust = 0.5)) +
  scale_fill_discrete('author\ngender\n') +
  scale_shape_manual('author\ngender\n', values = c(21, 22)) +
  scale_y_continuous('predictive accuracy\n', labels = percent) +
  xlab('') + ggtitle('Accuracy of character-gender predictions, made within\ngroups of characters drawn from authors of the same gender\n')
plot(p)
        