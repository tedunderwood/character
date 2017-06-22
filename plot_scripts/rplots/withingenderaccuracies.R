# withinauthorgender.R

within <- read.csv('/Users/tunder/Dropbox/python/character/withingenderaccuracies.csv')
p <- ggplot(within, aes(x = date, y = accuracy, color = author.gender, shape = author.gender)) + 
  geom_point(size = 4) +theme(text = element_text(size = 18)) + geom_line() +
  scale_color_manual(values = c('blue', 'red2')) +
  scale_x_continuous('') + scale_y_continuous('median accuracy of predictions about characters') +
  ggtitle('Accuracy of character-gender predictions made within\ncharacter sets drawn from authors of one gender\n')
plot(p)