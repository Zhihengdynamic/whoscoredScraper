# Master Thesis
# Jonathan Klaiber
# created 05.03.2016
# last modified: 05.03.2016
set.seed(123)

#internal functions
source('Progressor.R')

data <- read.csv('player_stats_validated.csv', encoding = 'UTF-8', 
                 stringsAsFactors = FALSE)

data <- subset(data, season == '2014-2015')

# Develop the different sub indices

#Subindex 1: Modelling Match Outcome

#Subindex 2: Points-Sharing Index

# Description:
# points awarded to a player in a match on
# subindex 2, I2, is given by the product of the points
# won by the team and the ratio of the number of minutes
# played by the player to the total number of minutes
# played by the entire team, including substitutes

I2 <- function(data) {
  matches <- unique(data$matchID)
  outputDF <- data.frame()
  p <- 1
  # loop through all matches in data
  for(match in matches) {
    # make dataframe for name and points per match
    matchDF <- data.frame()
    currentData <- subset(data, matchID == match)
    # compute points for home and away team
    for(loc in c('home', 'away')) {
      # points earned by the team
      points <- subset(currentData, pitch == loc)$pointsWon[1]
      # total minutes played including subsitutes
      totalMinutes <- sum(subset(currentData, pitch == loc)$playedMinutes)
      for(i in 1:dim(currentData)[1]) {
        # get player name
        name <- currentData$name[i]
        # get player ratio
        ratio <- currentData$playedMinutes[i] / totalMinutes
        # product of ratio and points for game is the I2
        pointsI2 <- points * ratio
        matchDF <- rbind(matchDF, data.frame(name = name, points = pointsI2,
                                             stringsAsFactors = FALSE))
      }
    }
    # put info of players into output dataframe
    for(j in 1:dim(matchDF)[1]) {
      if(!(matchDF$name[j] %in% outputDF$name)) {
        # make new entry in outputDF if player does not exist already or ...
        outputDF <- rbind(outputDF, matchDF[j,])
      } else {
        # update points of player
        nameIndex <- which(outputDF$name == matchDF$name[j])
        outputDF$points[nameIndex] <- (outputDF$points[nameIndex] 
                                        + matchDF$points[j])
      }
    }
    # montiors progress
    Progressor(p, length(matches))
    p <- p + 1
  }
  return(outputDF)
}

#example
season2014 <- I2(data)
#quick check
View(season2014[order(season2014$points, decreasing = TRUE), ])



#Subindex 3: Appearance Index

#Description:
# This subindex divides the number of points won by
# all teams in the league among the players according
# to how many minutes they played. In contrast to I2,
# this subindex does not take the won points into consideration.

# The average number of points won in any
# one game by any one team is 1.38 (calculated on
# the basis of data from the past 6 Bundesliga seasons)
# (This was 1.34 for the premiere league which means there 
# are more ties in the premier league than in the Bundesliga)
gamePointAverage <- mean(data$pointsWon)

I3 <- function(data) {
  matches <- unique(data$matchID)
  outputDF <- data.frame()
  p <- 1
  # loop through all matches in data
  teamDF <- data.frame()
  for(match in matches) {
    # make dataframe for name and points per match
    matchDF <- data.frame()
    currentData <- subset(data, matchID == match)
    # compute minutes for home and away team
    for(loc in c('home', 'away')) {
      # total minutes played including subsitutes
      totalMinutes <- sum(subset(currentData, pitch == loc)$playedMinutes)
      currentTeam <- subset(currentData, pitch == loc)$team[1]
      if(!(currentTeam %in% teamDF$team)) {
        # make new entry in outputDF if player does not exist already or ...
        teamdf <- data.frame(team = currentTeam,
                             totalMinutes = totalMinutes,
                             stringsAsFactors = FALSE)
        teamDF <- rbind(teamDF, teamdf)
      } else {
        # update points of player
        nameIndex <- which(teamDF$team == currentTeam)
        teamDF$totalMinutes[nameIndex] <- (teamDF$totalMinutes[nameIndex]
                                      + totalMinutes)
      }
      
      for(i in 1:dim(currentData)[1]) {
        # get player name
        name <- currentData$name[i]
        # get player ratio
        minutes <- currentData$playedMinutes[i]
        # product of ratio and points for game is the I2
        matchDF <- rbind(matchDF, data.frame(name = name, 
                                             minutes = minutes,
                                             team = currentTeam,
                                             stringsAsFactors = FALSE))
      }
    }
    # put info of players into output dataframe
    for(j in 1:dim(matchDF)[1]) {
      if(!(matchDF$name[j] %in% outputDF$name)) {
        # make new entry in outputDF if player does not exist already or ...
        outputDF <- rbind(outputDF, matchDF[j,])
      } else {
        # update points of player
        nameIndex <- which(outputDF$name == matchDF$name[j])
        outputDF$minutes[nameIndex] <- (outputDF$minutes[nameIndex] 
                                       + matchDF$minutes[j])
      }
    }
    # montiors progress
    Progressor(p, length(matches))
    p <- p + 1
  }
  
  # ratio of number of minutes played by the player to total
  # number of minutes played by the entire team, multiplyed by
  # gamePointAverage
  
  for(k in 1:dim(outputDF)[1]) {
    totalMins <- subset(teamDF, team == outputDF$team[k])$totalMinutes
    outputDF$ratio[k] <- outputDF$minutes[k] / totalMins
    outputDF$points[k] <-  (outputDF$minutes[k] / totalMins) * gamePointAverage
  }
  return(outputDF)
}

#example
season2014I3 <- I3(data)
#quick check
View(season2014I3[order(season2014I3$points, decreasing = TRUE), ])
