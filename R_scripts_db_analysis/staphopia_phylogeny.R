#Identify a set of strains from the DB.  Produce a phylogeny.
library("dplyr")
library("Biostrings")
library("assertthat")
source("~/.staphopia_logon.R")
db <- staphopia_logon()

########FUNCTIONS
pull_SNPs_by_strain <-function(strain_name){
  ids <- filter(snp_ids_tread,strain == strain_name) %>% select(snp_id) %>% collect()
  alt.df <- inner_join(ids,cleaned_pos, by = "snp_id") %>% select(snp_id,alternate_base) 
  return(alt.df)
}
create_string_set <- function(refDS,ref.df,strains) {
  DSS <-list(refDS)
  for (strain in strains) {
    temp.df <- pull_SNPs_by_strain(strain)
    temp2.df <- inner_join(ref.df,temp.df, by = "snp_id") %>% select(ct,alternate_base,snp_id)
    temp3 <- replaceLetterAt(refDS,temp2.df$ct,temp2.df$alternate_base)
    DSS <- append(DSS,temp3)
  }
  names(DSS) <- c("reference",strains)
  return(DSS)
}

########
#ena_exp <- tbl(db,"ena_experiment")
#sample_accs <- filter(ena_exp,study_accession == "PRJNA239001") %>% select(sample_accession)

#open tables
samples_tab <-tbl(db,"samples_sample")
anal_var_tab <-tbl(db,"analysis_variant")
anal_var_tosnp_tab <- tbl(db,"analysis_varianttosnp") %>%
  select(id,quality,comment_id,snp_id,variant_id)
anal_variantSNP <- tbl(db,"analysis_variantsnp") %>%
  select(id,alternate_base,reference_base,reference_position)
anal_var_toindel_tab <- tbl(db,"analysis_varianttoindel") %>%
  select(id,indel_id,variant_id)
anal_variantindel <- tbl(db,"analysis_variantindel") %>%
  select(id,alternate_base,reference_base,reference_position,is_deletion)

#find all the SNPs from all the projects tagged with NARSA
tread_samples <-filter(samples_tab, sql("comments ILIKE '%NARSA%'")) %>% #note dplyr cant do ILIKE or LIKE statements so need to substitute sql
  select(id,strain)
anal_var_tab_tread <- inner_join(tread_samples,anal_var_tab, by = c("id" = "sample_id")) %>%
  select(id.y,strain)  # note - could also filter here for the veriosn number
snp_ids_tread <-inner_join(anal_var_tosnp_tab,anal_var_tab_tread, by = c("variant_id" = "id.y"))

# identity the minimal set and the SNPs involved
snp_id_list <- select(snp_ids_tread,snp_id) %>% group_by(snp_id) %>% filter(row_number() == 1)
ref_pos <- inner_join(anal_variantSNP,snp_id_list, by = c("id" = "snp_id")) %>% collect()

#similarly, find all the indels and get the minimal set

indel_ids_tread <-inner_join(anal_var_toindel_tab,anal_var_tab_tread, by = c("variant_id" = "id.y"))
indel_list <- select(indel_ids_tread,indel_id) %>% group_by(indel_id) %>% filter(row_number() == 1)
indel_pos <- inner_join(anal_variantindel,indel_list, by = c("id" = "indel_id")) %>% collect()
#
#remove all snps that are i the asme referecne position as an indel
cleaned_pos <- filter(ref_pos,!(reference_position %in% indel_pos$reference_position))
N315.df <-  select(cleaned_pos,reference_base,reference_position,snp_id)
assert_that(not_empty(N315.df))

#now identify all snps that overlap with indels
#pos_to_be_removed <- filter(N315.df,reference_position %in% indel_pos$reference_position)


N315.df <- cbind(N315.df,1:nrow(N315.df)) #add explicit row number
colnames(N315.df)[4] <- "ct"
N315 <- DNAString(paste(N315.df$reference_base,sep = "",collapse = ""))

### now pull down the SNPs for the individual strains and replace
sample_names <- collect(tread_samples)
seqDSS <- create_string_set(N315,N315.df,sample_names$strain)

## tidy up and output
names(seqDSS)[1] <- "N315_ref"
seqDSSet <- DNAStringSet(seqDSS)

##now remove te indels
#pos_to_be_removed <- filter(N315.df,reference_position %in% indel_pos$reference_position)




writeXStringSet(seqDSSet,"./aligned_Sa.fasta",format = "fasta")



