library(ggplot2)
library(scales)
library(dplyr)
data=read.table("plot_data/authorcharacter.txt", sep="\t")
gdf=as.data.frame(data)
gdf <- filter(gdf, V1 > 1849)
p <- ggplot(gdf, (aes(x=gdf$V1))) +  geom_ribbon(data=gdf, aes(ymin=gdf$V2, ymax=gdf$V4), fill=alpha("orange",0.2), col=alpha("black",0.3)) + 
  geom_point(data=gdf, aes(x=gdf$V1, y=gdf$V3), size=1) + geom_point(data=gdf, aes(x=gdf$V1, y=gdf$V6), size=1) + geom_ribbon(data=gdf, aes(ymin=gdf$V5, ymax=gdf$V7), fill=alpha("blue",0.2), col=alpha("black",0.3)) + xlab("") + ylab("") + 
  ggtitle("Description of women, as a percentage of characterization,\n broken out by author gender") + 
  scale_y_continuous(labels = scales::percent, limits=c(0,.65)) +
  theme(text = element_text(size = 14)) + 
  theme(plot.title = element_text(hjust = 0.5)) +
  theme(plot.title = element_text(size = 14))
plot(p)