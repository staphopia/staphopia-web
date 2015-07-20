#Identify a set of strains from the DB.  Produce a phylogeny.
library("dplyr")
source("~/.staphopia_logon.R")
db <- staphopia_logon()
#ena_exp <- tbl(db,"ena_experiment")
#sample_accs <- filter(ena_exp,study_accession == "PRJNA239001") %>% select(sample_accession)

#open tables
samples_tab <-tbl(db,"samples_sample")
anal_var_tab <-tbl(db,"analysis_variant")
anal_var_tosnp_tab <- tbl(db,"analysis_varianttosnp") %>%
  select(id,quality,comment_id,snp_id,variant_id)

#find all the SNPs from all the projects
tread_samples <-filter(samples_tab, sql("comments ILIKE '%NARSA%'")) %>% #note dplyr cant do ILIKE or LIKE statements so need to substitute sql
  select(id,strain)
anal_var_tab_tread <- inner_join(tread_samples,anal_var_tab, by = c("id" = "sample_id")) %>%
  select(id.y,strain)  # note - could also filter here for the veriosn number
snp_ids_tread <-inner_join(anal_var_tosnp_tab,anal_var_tab_tread, by = c("variant_id" = "id.y"))