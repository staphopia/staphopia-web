#Identify a set of strains from the DB.  Produce a phylogeny.
library("dplyr")
library("Biostrings")
library("assertthat")
source("~/.staphopia_logon.R")
db <- staphopia_logon()
#ena_exp <- tbl(db,"ena_experiment")
#sample_accs <- filter(ena_exp,study_accession == "PRJNA239001") %>% select(sample_accession)

#open tables
samples_tab <-tbl(db,"samples_sample")
anal_var_tab <-tbl(db,"analysis_variant")
anal_var_tosnp_tab <- tbl(db,"analysis_varianttosnp") %>%
  select(id,quality,comment_id,snp_id,variant_id)
anal_variantSNP <- tbl(db,"analysis_variantsnp") %>%
  select(id,alternate_base,reference_base,reference_position)

#find all the SNPs from all the projects tagged with NARSA
tread_samples <-filter(samples_tab, sql("comments ILIKE '%NARSA%'")) %>% #note dplyr cant do ILIKE or LIKE statements so need to substitute sql
  select(id,strain)
anal_var_tab_tread <- inner_join(tread_samples,anal_var_tab, by = c("id" = "sample_id")) %>%
  select(id.y,strain)  # note - could also filter here for the veriosn number
snp_ids_tread <-inner_join(anal_var_tosnp_tab,anal_var_tab_tread, by = c("variant_id" = "id.y"))

# identity the minimal set and the SNPs involved
snp_id_list <- select(snp_id_list,snp_id) %>% group_by(snp_id) %>% filter(row_number() == 1)
ref_pos <- inner_join(anal_variantSNP,snp_id_list, by = c("id" = "snp_id"))

# download reference DNA string  (note, its already ordered by reference position)
N315.df <- select(ref_pos,reference_base,snp_id) %>% collect()
N315 <- DNAString(paste(N315.df$reference_base,sep = "",collapse = ""))
#add assertion here



assert_that(is.data.frame(N315.df))

pull_SNPs_by_strain <-function(strain_name){
  ids <- filter(snp_ids_tread,strain == strain_name) %>% select(snp_id)
  alt.df <- inner_join(ids,ref_pos, by = "snp_id") %>% select(snp_id,alternate_base) %>% collect()
  return(alt.df)
}
temp.df <- pull_SNPs_by_strain("NRS218")