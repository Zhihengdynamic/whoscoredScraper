library("ggplot2")
plotRatingDist <- function(ratingDat, title) {
  ratingDat <- subset(ratingDat, !is.na(rating))
  binWidth <- sd(ratingDat$rating, na.rm = TRUE) / 5
  lower <- floor(min(ratingDat$rating, na.rm = TRUE))
  upper <- ceiling(max(ratingDat$rating, na.rm = TRUE))
  len <- ceiling(binWidth * sum(!is.na(ratingDat$rating)))
  plotTitle <- paste0("Distribution of ", title,
                      "\n End-Of-Season Ratings BL15/16")
  while(len %% 5 != 0) {len <- len + 0.5}
  
  ratingDatHist <- (ggplot(ratingDat, aes(x = rating)) 
               + geom_histogram(binwidth = binWidth,
                                fill="darkblue",
                                col = 'grey',
                                xlim = c(lower, upper)))
  
  histBuild <- ggplot_build(ratingDatHist)
  # create text
  rounDec <- 2
  meanText <- paste0('Mean (SD): ', round(mean(ratingDat$rating,
                                          na.rm = TRUE), rounDec),
                     ' (', round(sd(ratingDat$rating,
                                        na.rm = TRUE), rounDec),')')
  minText <- paste0('Min: ', round(quantile(ratingDat$rating,
                                            na.rm = TRUE)[1], rounDec))
  medianText <- paste0('Median: ', round(quantile(ratingDat$rating,
                                                  na.rm = TRUE)[3], rounDec))
  maxText <- paste0('Max: ', round(quantile(ratingDat$rating,
                                            na.rm = TRUE)[5], rounDec))
  ratedDaysText <- paste0('Rated Games Mean: ', round(mean(ratingDat$gamesRated,
                                                          na.rm = TRUE), rounDec))
  ratedDaysTextMed <- paste0('Rated Games Median: ', round(median(ratingDat$gamesRated,
                                                          na.rm = TRUE), rounDec))
  totalText <- paste0('Rated Players: ', round(length(ratingDat$rating), rounDec))

  outputTxt <- paste0(c(meanText,
                     minText,
                     medianText,
                     maxText,
                     ratedDaysText,
                     ratedDaysTextMed,
                     totalText), collapse = '\n')
  
  xTextScaling <- 0
  if(grepl('PPI', title)) {
    xTextScaling <- histBuild$panel$ranges[[1]]$x.range[2] * 0.5
  }
  
  (ratingDatHist
  + scale_x_continuous("Rating", 
                       breaks = round(seq(lower, upper, (upper - lower) / 8)))
  + scale_y_discrete("Count", 
                     breaks = round(
                       seq(0, 
                           histBuild$panel$ranges[[1]]$y.range[2],
                       length.out = 6)))
  #, breaks = round(seq(0, len, length = 6))
  + ggtitle(plotTitle)
  + stat_function(
    fun = function(x, mean, sd, n, binWidth){
      binWidth * n * dnorm(x = x, mean = mean, sd = sd)
    }, 
    args = with(ratingDat, c(mean = mean(rating, na.rm = TRUE), 
                             sd = sd(rating, na.rm = TRUE),
                        n  = length(rating),
                        binWidth = binWidth)))
  + annotate(geom = "text", 
             x = xTextScaling,
             y = histBuild$panel$ranges[[1]]$y.range[2] * 0.8,
             #y = Inf,
             label = outputTxt,
             hjust = 0,
             vjust = 1,
             size = 7)
  + theme(plot.title = element_text(lineheight = .8, face = "bold", 
                                    size = 18),
          #text = element_text(size = 8),
          axis.text.x = element_text(size = 15),
          axis.text.y = element_text(size = 15),
          axis.title.x = element_text(size = 20),
          axis.title.y = element_text(size = 20))
  )
}