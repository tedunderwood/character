errors <- read.csv('/Users/tunder/Dropbox/python/character/dataforR/pubweeklyerrorbars.csv')
hathi <- read.csv('/Users/tunder/Dropbox/python/character/dataforR/authorratios.csv')
p <- ggplot() + 
  geom_errorbar(data=errors, mapping=aes(x=year, ymin=low, ymax=high), width=5, size=1, color="blue") + 
  geom_point(data=errors, mapping=aes(x=year, y=mean), size=4, shape=21, fill="white") +
  geom_line(data = hathi, mapping = aes(x = year, y = authratio)) + 
  ylab('fraction of books by women') +
  xlab('') +
  ggtitle('Fraction of books by women in HathiTrust (line)\nand Publishers Weekly (error bars)\n') +
  xlim(1850, 2007) + ylim(0, 0.65)
plot(p)