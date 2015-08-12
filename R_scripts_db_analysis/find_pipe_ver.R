#' Returns a dataframe with the most current version number of all the Staphopia analysis pipelines
#'
#' @param db Staphopia db handle.
#'
#' @return
#' @export
#'
#' @examples
find_pipe_ver <- function(db){
  library(dplyr)
  pipelineversion_tab <- tbl(db,"analysis_pipelineversion")
  max_ids <- group_by(pipelineversion_tab, module) %>% summarise(max(id)) %>% collect()
  return(max_ids)
}