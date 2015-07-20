#develop methods using dplyr and output basic summaries of the database
library("dplyr")
source("~/.staphopia_logon.R")
db <- staphopia_logon()
samples_tab <-tbl(db,"samples_sample")
# top genome centers
top_20_sc <- count(samples_tab, sequencing_center) %>% top_n(20) %>% as.data.frame



#number that are published
num_pub <- count(samples_tab,is_published) %>% as.data.frame
#breakdown of gold, silver, bronze

#breakdown of N50, number of contigs

#SNPs versus numbers of genomes

#breakdown of sequencing methods (Illumina, PacBio etc)

#If Illumina then paried end versus single, length of run

#year of sequencing

#year of isolation
