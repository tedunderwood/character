areas <- read.csv('~/Dropbox/python/character/dataforR/nonfiction_stack_graph.csv')

p = ggplot(areas, aes(x=year, y=fraction, fill=genre)) + 
  ylab('fraction of all books') + xlab('') +
  geom_area() + scale_fill_manual(values = c('firebrick1', 'navy')) +
  ggtitle('Books by women, as a fraction of all books\n')

  plot(p)