source('~/staphopia.com/R_scripts_db_analysis/pull_ids.R', chdir = TRUE)
library(testthat)
library(dplyr)

test_that("database internal ids have not changed since August 2015",{
  expect_that(filter(samples_tab,id == 1) 
              %>% select(sample_tag) 
              %>% collect() 
              %>% as.character(),equals("ERX006681"))
  
})