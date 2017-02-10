# 
# Infer gender and race from names via alternate methods
#

# set dir.
setwd(githubdir)
setwd("tv_schedules/")

# load libs
library(dplyr)
library(stringr)
library(gender)
library(genderdata)
#devtools::install_github("soodoku/ethnicolor")
library(ethnicolor)

# read in data
tv_names <- read.csv("data/us_tv_schedules_names.csv")

# split name into first and last name
tv_names$first_name <-  word(tv_names$name, 1)
tv_names$last_name  <-  word(tv_names$name, -1)

# Infer gender based on first name
tv_names$min_year <- 1940
tv_names$max_year <- 1990

# Get gender 
fname_gender <- gender_df(tv_names, name_col="first_name", year_col = c("min_year", "max_year"), method="ssa")


# Merge 

names(tv_names)[match(c("race", "gender"), names(tv_names))] <- c("py_race", "py_gender")

tv_names_gender <- 
	tv_names %>%
	left_join(fname_gender,  c("first_name" = "name"))

# Infer race based on last name/Only for unique
lname_unique <- unique(tv_names$last_name)
lname_race   <- cs_surname(lname_unique)

# Merge All
tv_names_gender$last_name <- tolower(tv_names_gender$last_name)

tv_names_race_gender <- 
	tv_names_gender %>%
	left_join(lname_race, c("last_name" = "name"))

# Write out 
write.csv(tv_names_race_gender, file="data/tv_names_race_gender.csv", row.names=F)