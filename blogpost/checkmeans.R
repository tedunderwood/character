library(dplyr)
unk <- read.csv('/Users/tunder/Dropbox/python/character/vizdata/manually_corrected_genders.csv')
unk <- arrange(unk, inferreddate)
genders <- rep(0, length(unk$realgender))
genders[unk$realgender == 'm'] <- 1
genders[unk$realgender == 'f'] < -1
genders[unk$realgender == 'u'] <- NA

for (i in seq(1, length(genders), 12)) {
  meangender = mean(genders[i : (i + 12)], na.rm = TRUE)
  meandate = mean(unk$inferreddate[i : (i+ 12)])
  print(meangender)
  print(meandate)
  print('-')
}

