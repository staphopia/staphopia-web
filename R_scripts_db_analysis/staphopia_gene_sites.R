#list all the sites that fall in a single gene.  Optionally, limit output to a strain or set of strains
library("dplyr")
source("~/.staphopia_logon.R")
db <- staphopia_logon()