library("dplyr")
source("~/.staphopia_logon.R")
db <- staphopia_logon()
samples_tab <-tbl(db,"samples_sample")
top_20_sc <- count(samples_tab, sequencing_center) %>% top_n(20)

