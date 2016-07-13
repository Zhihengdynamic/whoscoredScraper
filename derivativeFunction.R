derivativeFunction <- function(varName, path) {
  # function to evaluate derivative of a given player action
  # load derivative data
  singleString <- paste(readLines(paste0(path,
                                         '/derivatives/',
                                         varName,
                                         '.txt')), collapse=" ")
  # replace values in string to make them compatible with R
  #eqString <- gsub("Exp\\*", "", singleString)
  eqString <- gsub("*^", "e", singleString, fixed = TRUE)
  
  while (grepl('  ', eqString)) {
    eqString <- gsub('  ', ' ', eqString)
  }
  
  # split derivatives in three meaningful parts (part 2 and 3 depend on 
  # home and away team)
  firstSplit <- strsplit(eqString, "))*", fixed = TRUE)[[1]]
  # remove exponentional
  part1 <- gsub("Exp\\*", "", paste0(firstSplit[1], "))"))
  # add exponential
  part1Res <- eval(parse(text=part1))
  
  # split again based on the exp part
  restPart2 <- firstSplit[2]
  secondSplit <- strsplit(restPart2, "Exp\\*")[[1]]
  
  if(grepl('hCross', varName)|
     grepl('hPass', varName)|
     grepl('hDribbel', varName)|
     grepl('aInter', varName)|
     grepl('aYellow', varName)|
     grepl('aRed', varName)|
     grepl('aTackle', varName)|
     grepl('aCleared', varName)) {
    # the split for home and away is different:
    part2 <- strsplit(secondSplit[1], '^10)', fixed = TRUE)[[1]][1]
    part2 <- paste0(part2, '^10)')
    part3Multiply <- strsplit(secondSplit[1], '^10)', fixed = TRUE)[[1]][2]
    part3Multiply <- gsub('\\*', '', part3Multiply)
  } else {
    # the split is different for the neg. coefficient hInter and hTackle
    splitSign <- ifelse(varName %in% c('hInter', 'hTackle'), '+', '-')
    part2 <- strsplit(secondSplit[1], 
                      paste0('^9) ', splitSign), fixed = TRUE)[[1]][1]
    # get the second part
    part2 <- paste0(part2, '^9)')
    # get factor multiplication value
    part3Multiply <- strsplit(secondSplit[1], 
                              paste0('^9) ', splitSign), fixed = TRUE)[[1]][2]
    part3Multiply <- paste0(splitSign, gsub('\\*', '', part3Multiply))
  }
  
  # compute part 2 values
  part2Res <- eval(parse(text = part2))
  
  # compute part 3 values and multiply with factor
  part3 <- secondSplit[2]
  part3Res <- eval(parse(text = part3Multiply)) * eval(parse(text = part3))
  
  # combine all results, all parts have to be expontiated because
  # in mathematica there is a multiplication Exp
  finalRes <- exp((part1Res * part2Res) + part3Res)
  
  # compared with Mathematica (and validated):
  #hCross 
  #hDribbel
  #hPass
  #aInter
  #aYellow
  #aRed
  #aCleared
  #aTackle
  
  #aCross
  #aPass
  #aDribbel
  #hInter
  #hYellow
  #hRed
  #hTackle
  #hCleared
  
  return(finalRes)
}