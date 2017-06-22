gr <- gw$total / (gw$total + bw$total)
br <- gm$total / (gm$total + bm$total)
girlratio = c()
boyratio = c()
for (i in seq(1880, 1990)) {
  girlratio = c(girlratio, mean(gr[gm$date == i]))
  boyratio = c(boyratio, mean(br[gm$date == i]))
}
df <- data.frame(date = rep(gm$date[gm$date > 1879 & gm$date < 1991],2), womenratio = c(boyratio[bm$date > 1879 & bm$date < 1991], 
          girlratio[gm$date > 1879 & gm$date < 1991]), author.gender = c(rep('men', 111), rep('women', 111)) )
p <- ggplot(df, aes(x = date, y = womenratio, group = author.gender, colour = author.gender)) + 
  geom_point() + scale_x_continuous("") + 
  scale_y_continuous("words about women", labels=percent) +
  ggtitle('Words about women, as a percentage\nof all characterization\n')
plot(p)