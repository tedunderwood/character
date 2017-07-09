library(ggplot2)
library(dplyr)
library(reshape2)

df <- read.csv('/Users/tunder/Dropbox/python/character/dataforR/diff_matrix.csv')
df <- df[df$thedate > 1799, ]

subset <- select(df, thedate, eyes, hair, chest, pocket)

longform <- melt(subset, id.vars = c('thedate'))

p <- ggplot(longform, aes(x = thedate, y = value, color = variable, shape = variable)) + geom_point() + geom_smooth(span = 0.6, se = FALSE) +
  scale_color_manual(name = "word\n", values = c('gray40', 'red2', 'dodgerblue', 'olivedrab')) +
  theme(text = element_text(size = 16)) + scale_shape(name="word\n") +
  scale_y_continuous('Uses for women, minus uses for men,\n in 10k words selected equally from both\n', limits = c(-10, 34)) + 
  scale_x_continuous("", breaks = c(1800,1850,1900,1950,2000))

plot(p)