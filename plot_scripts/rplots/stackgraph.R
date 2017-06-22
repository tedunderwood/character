best <- read.csv('/Users/tunder/Dropbox/python/character/charbyyearandauthgender.csv')
boysbymen = c()
girlsbymen = c()
boysbywomen = c()
girlsbywomen = c()

bm = filter(best, authgender == 'm', chargender == 'm')
gm = filter(best, authgender == 'm', chargender == 'f')
bw = filter(best, authgender == 'f', chargender == 'm')
gw = filter(best, authgender == 'f', chargender == 'f')

for i in range(1922, 2010, 2) {
  thisbm = bm$total[bm$date == i] + bm$total[bm$date == i+1]
  thisgm = gm$total[gm$date == i] + gm$total[gm$date == i+1]
  thisbw =  bw$total[bw$date == i] + bw$total[bw$date == i+1]
  thisgw = gw$total[gw$date == i] + gw$total[gw$date == i+1]
  total = thisbm + thisgm +thisbw + thisgw
  
  boysbymen = c(boysbymen, thisbm/total)
  girlsbymen = c(girlsbymen, thisgm/total)
  boysbywomen = c(boysbywomen,thisbw/total)
  girlsbywomen = c(girlsbywomen, thisgwtotal)
  
  
}

