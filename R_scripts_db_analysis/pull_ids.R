#' Function to query the Staphopia database by a particular term and return a useful table of strain info
#' 
#' @param db 
#' @param strain_name 
#' @param comments 
#' @param project 
#' @param STtype 
#' @param mlstpl 
#'
#' @return
#' @export
#'
#' @examples
#' P <- pull_ids(db,project = "PRJNA239001")
pull_ids <-function(db,strain_name = NA,comments = NA,project = NA, STtype = NA,mlstpl = NA){
  library("dplyr")
  library("assertthat")
  assert_that(sum(!is.na(c(strain_name,comments,project,STtype))) == 1) #need to add a message
  #open tables
  samples_tab <-tbl(db,"samples_sample")
  mlst_tab <- tbl(db,"analysis_mlst")
  mlstsrst2_tab <- tbl(db,"analysis_mlstsrst2")
  experiment_tab <-  tbl(db,"ena_experiment")
  pipelineversion_tab <- tbl(db,"analysis_pipelineversion")
  #default to the most up to date version of the mlst pipeline (this should be a function one day)
  if (is.na(mlstpl)) {
  mlstpl <- filter(pipelineversion_tab, module== "mlst") %>% summarise(max(id))%>% collect() %>% as.character()
  }
  else {
    as.character(mlstpl)
  }
  #join_tables
  mlst_ST_tab <- inner_join(mlst_tab,mlstsrst2_tab, by = c("id" = "mlst_id")) %>% filter(version_id == mlstpl)
  mlst_strain_tab <- left_join(samples_tab,mlst_ST_tab, by = c("id" = "sample_id")) %>% select(id, sample_tag, comments,strain, ST)
  mlst_strain_ena_tab <- left_join(mlst_strain_tab,experiment_tab, by = c("sample_tag" = "experiment_accession")) %>%
    select(id, sample_tag, comments,strain, ST, study_accession)
  #filter by query
  if (!is.na(strain_name)) {
    strain_name <- as.character(strain_name)
    sql_string <- paste("strain ILIKE \'%",strain_name, "%\'",sep = "")
    res_table <-filter(mlst_strain_ena_tab, sql(sql_string))
  }
  else if (!is.na(comments)) {
    comments <- as.character(comments)
    sql_string <- paste("comments ILIKE \'%",comments, "%\'",sep = "")
    res_table <-filter(mlst_strain_ena_tab, sql(sql_string))
  }
  else if (!is.na(project))  {
    project <- as.character(project)
    sql_string <- paste("study_accession ILIKE \'%",project, "%\'",sep = "")
    res_table <-filter(mlst_strain_ena_tab, sql(sql_string))
  }
  else if (!is.na(STtype)) {
    STtype <- as.character(STtype)
    res_table <-filter(mlst_strain_ena_tab, ST == STtype)
  }
  return(res_table)
}

