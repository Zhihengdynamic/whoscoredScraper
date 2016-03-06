# Simple function to monitor progress
Progressor <- function(i, iMax) {
  cat("\r Completed:", paste0(round(i / iMax, 2) * 100, "%"))
  flush.console()
}