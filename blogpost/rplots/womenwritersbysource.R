library(ggplot2)
library(scales)
library(dplyr)

hathi <- read.csv('/Users/tunder/Dropbox/python/character/corrected_hathi_summaries.csv')
hathi <- arrange(hathi, date)
hathi <- filter(hathi, date < 2008, date > 1799)

onlyboys <- filter(hathi, authgender == 'm')
boysbyyear <- group_by(onlyboys, date)
boysperyear <- summarise(boysbyyear, total = sum(total))
onlygirls <- filter(hathi, authgender == 'f')
girlsbyyear <- group_by(onlygirls, date)
girlsperyear <- summarise(girlsbyyear, total = sum(total))

if (length(girlsperyear$date) == length(boysperyear$date)) hathidates = girlsperyear$date

hathiratio <- (girlsperyear$total) / (girlsperyear$total + boysperyear$total)

chicago <-read.csv('/Users/tunder/Dropbox/python/character/chicago/chicago_summary.csv')

chic <- arrange(chicago, date)

onlyboys <- filter(chic, authgender == 'm')
boysbyyear <- group_by(onlyboys, date)
boysperyear <- summarise(boysbyyear, total = sum(total))
onlygirls <- filter(chic, authgender == 'f')
girlsbyyear <- group_by(onlygirls, date)
girlsperyear <- summarise(girlsbyyear, total = sum(total))

if (length(girlsperyear$date) == length(boysperyear$date)) chidates = girlsperyear$date

chicagoratio <- (girlsperyear$total) / (girlsperyear$total + boysperyear$total)

df <- data.frame(date = c(hathidates, chidates), 
                 womenratio = c(hathiratio, chicagoratio), 
                 source = as.factor(c(rep('Hathi', length(hathidates)), rep('Chicago', length(chidates)))) )
p <- ggplot(df, aes(x = date, y = womenratio, color = source)) + 
  geom_point(aes(color = source)) + scale_x_continuous("") + 
  scale_colour_manual(values = c('red2', 'gray30')) + theme(text = element_text(size = 20)) + 
  scale_y_continuous("", labels=percent, limits = c(0, 0.6)) +
  ggtitle('Words written by women, as a percentage\nof characterization\n')
plot(p)