"

Plots of TV Shows!

"

# Set dir
setwd(githubdir)
setwd("tv_schedules/")

# Load libs
library(dplyr)
library(magrittr)
library(ggplot2)

# Read in data
race_gender  <- read.csv("data/us_tv_schedules_prop_R.csv")
tv_schedules <- read.csv("data/us_tv_schedules_meta.csv")

# Cust Theme for the Plot
cust_theme <- 
theme_minimal() +
theme(panel.grid.major  = element_line(color="#e7e7e7",  linetype = "dotted", size=.25),
	  panel.grid.minor  =  element_blank(),
	  legend.position   = "none",
	  axis.title   = element_text(size=10, color="#555555"),
	  axis.text    = element_text(size=8, color="#555555"),
	  axis.ticks.y = element_blank(),
	  axis.title.x = element_text(vjust=-1),
	  axis.title.y = element_text(vjust= 1),
	  axis.ticks.x = element_line(color="#e7e7e7",  linetype = "dotted", size=.2),
	  plot.margin = unit(c(0,1,.5,.5), "cm"))

# Handling year
tv_schedules$start_year <- as.numeric(substr(tv_schedules$year, 1, 4)) 
race_gender$start_year  <- as.numeric(substr(race_gender$year, 1, 4))

# Handle Genre 
tv_schedules$crime[grepl("Crime|Police|Detective", tv_schedules$genre)] <- 1

# Genre Over time 
out <- 
tv_schedules %>%
group_by(start_year) %>%
summarise(crime = sum(crime, na.rm=T), n = n(), pcrime = crime/n)

ggplot(out, aes(x=start_year, y=pcrime*100)) + 
geom_line(color="#d3d3d3", size = .25, alpha=.7) + 
geom_point(pch=16, size=1, color="#9ebcda", alpha=.7) + 
scale_y_continuous(name="Percentage of Crime Shows", limits=c(0,100), breaks=seq(0,100,10), labels=paste0(seq(0,100,10), "%")) +
scale_x_continuous(name="", limits=c(1945, 2016), breaks=seq(1945, 2016, 5), labels=seq(1945, 2016, 5)) +
cust_theme
ggsave("figs/crime_over_time.pdf")
ggsave("figs/crime_over_time.png", height=2.5)


# Race and Gender
# ------------------------
# Percentage of Black Producers Over Time
ggplot(race_gender, aes(x=start_year, y=prop_black_producers*100)) + 
geom_line(color="#d3d3d3", size = .25, alpha=.7) + 
geom_point(pch=16, size=1, color="#9ebcda", alpha=.7) + 
scale_y_continuous(name="Percentage of Black Producers", limits=c(0,100), breaks=seq(0,100,10), labels=paste0(seq(0,100,10), "%")) +
scale_x_continuous(name="", limits=c(1945, 2016), breaks=seq(1945, 2016, 5), labels=seq(1945, 2016, 5)) +
cust_theme

ggsave("figs/black_producers_over_time.pdf")
ggsave("figs/black_producers_over_time.png", height=3)

# Percentage of Black Directors Over Time
ggplot(race_gender, aes(x=start_year, y=prop_black_directors*100)) + 
geom_line(color="#d3d3d3", size = .25, alpha=.7) + 
geom_point(pch=16, size=1, color="#9ebcda", alpha=.7) + 
scale_y_continuous(name="Percentage of Black Directors", limits=c(0,100), breaks=seq(0,100,10), labels=paste0(seq(0,100,10), "%")) +
scale_x_continuous(name="", limits=c(1945, 2016), breaks=seq(1945, 2016, 5), labels=seq(1945, 2016, 5)) +
cust_theme

ggsave("figs/black_directors_over_time.pdf")
ggsave("figs/black_directors_over_time.png", height=3)

# Percentage of Black Cast Members Over Time

ggplot(race_gender, aes(x=start_year, y=prop_black_cast*100)) + 
geom_line(color="#d3d3d3", size = .25, alpha=.7) + 
geom_point(pch=16, size=1, color="#9ebcda", alpha=.7) + 
scale_y_continuous(name="Percentage of Black Cast Members", limits=c(0,100), breaks=seq(0,100,10), labels=paste0(seq(0,100,10), "%")) +
scale_x_continuous(name="", limits=c(1945, 2016), breaks=seq(1945, 2016, 5), labels=seq(1945, 2016, 5)) +
labs(color=NULL) + 
cust_theme

ggsave("figs/black_cast_members_over_time.pdf")
ggsave("figs/black_cast_members_over_time.png", height=3)

# Percentage of Black Presenters Over Time

ggplot(race_gender, aes(x=start_year, y=prop_black_presenters*100)) + 
geom_line(color="#d3d3d3", size = .25, alpha=.7) + 
geom_point(pch=16, size=1, color="#9ebcda", alpha=.7) + 
scale_y_continuous(name="Percentage of Black Presenters", limits=c(0,100), breaks=seq(0,100,10), labels=paste0(seq(0,100,10), "%")) +
scale_x_continuous(name="", limits=c(1945, 2016), breaks=seq(1945, 2016, 5), labels=seq(1945, 2016, 5)) +
labs(color=NULL) + 
cust_theme

ggsave("figs/black_presenters_over_time.pdf")
ggsave("figs/black_presenters_over_time.png", height=3)

# Percentage of Female Presenters Over Time

ggplot(race_gender, aes(x=start_year, y=prop_female_presenters*100)) + 
geom_line(color="#d3d3d3", size = .25, alpha=.7) + 
geom_point(pch=16, size=1, color="#9ebcda", alpha=.7) + 
scale_y_continuous(name="Percentage of Female Presenters", limits=c(0,100), breaks=seq(0,100,10), labels=paste0(seq(0,100,10), "%")) +
scale_x_continuous(name="", limits=c(1945, 2016), breaks=seq(1945, 2016, 5), labels=seq(1945, 2016, 5)) +
labs(color=NULL) + 
cust_theme

ggsave("figs/female_presenters_over_time.pdf")
ggsave("figs/female_presenters_over_time.png", height=3)

# Percentage of Female Producers Over Time

ggplot(race_gender, aes(x=start_year, y=prop_female_producers*100)) + 
geom_line(color="#d3d3d3", size = .25, alpha=.7) + 
geom_point(pch=16, size=1, color="#9ebcda", alpha=.7) + 
scale_y_continuous(name="Percentage of Female Producers", limits=c(0,100), breaks=seq(0,100,10), labels=paste0(seq(0,100,10), "%")) +
scale_x_continuous(name="", limits=c(1945, 2016), breaks=seq(1945, 2016, 5), labels=seq(1945, 2016, 5)) +
labs(color=NULL) + 
cust_theme

ggsave("figs/female_producers_over_time.pdf")
ggsave("figs/female_producers_over_time.png", height=3)

# Percentage of Female Directors Over Time

ggplot(race_gender, aes(x=start_year, y=prop_female_directors*100)) + 
geom_line(color="#d3d3d3", size = .25, alpha=.7) + 
geom_point(pch=16, size=1, color="#9ebcda", alpha=.7) + 
scale_y_continuous(name="Percentage of Female Directors", limits=c(0,100), breaks=seq(0,100,10), labels=paste0(seq(0,100,10), "%")) +
scale_x_continuous(name="", limits=c(1945, 2016), breaks=seq(1945, 2016, 5), labels=seq(1945, 2016, 5)) +
labs(color=NULL) + 
cust_theme

ggsave("figs/female_directors_over_time.pdf")
ggsave("figs/female_directors_over_time.png", height=3)

# Percentage of Female Cast Members Over Time

ggplot(race_gender, aes(x=start_year, y=prop_female_cast*100)) + 
geom_line(color="#d3d3d3", size = .25, alpha=.7) + 
geom_point(pch=16, size=1, color="#9ebcda", alpha=.7) + 
scale_y_continuous(name="Percentage of Female Cast Members", limits=c(0,100), breaks=seq(0,100,10), labels=paste0(seq(0,100,10), "%")) +
scale_x_continuous(name="", limits=c(1945, 2016), breaks=seq(1945, 2016, 5), labels=seq(1945, 2016, 5)) +
labs(color=NULL) + 
cust_theme

ggsave("figs/female_cast_members_over_time.pdf")
ggsave("figs/female_cast_members_over_time.png", height=3)

