# Master Thesis
# Jonathan Klaiber
# created 05.03.2016
# last modified: 05.03.2016
set.seed(123)

#internal functions
source('Progressor.R')

# View indices
viewIndices <- FALSE

# get path to repository
path <- unlist(read.table('repPath.txt'))

# load data from repository
data <- read.csv(file.path(path, 'player_stats_validated.csv'), 
                 encoding = 'UTF-8', 
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
        matchDF <- rbind(matchDF, data.frame(name = name, pointsI2 = pointsI2,
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
        outputDF$pointsI2[nameIndex] <- (outputDF$pointsI2[nameIndex] 
                                        + matchDF$pointsI2[j])
      }
    }
    # montiors progress
    Progressor(p, length(matches))
    p <- p + 1
  }
  return(outputDF)
}

#example
season2014I2 <- I2(data)
#quick check
if(viewIndices) {
  View(season2014I2[order(season2014I2$pointsI2, decreasing = TRUE), ])
}


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

I3 <- function(data, gamePointAverage) {
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
    outputDF$pointsI3[k] <-  (outputDF$minutes[k] / 
                                totalMins) * gamePointAverage
  }
  return(outputDF)
}

#example
season2014I3 <- I3(data, gamePointAverage)
#quick check
if(viewIndices) {
  View(season2014I3[order(season2014I3$pointsI3, decreasing = TRUE), ])
}

#Subindex 4: Goal-Scoring Index

# Description:
# The points awarded to a player in a
# match for goals, I4, is then simply the points per goal
# multiplied by the number of goals.

# compute points per goal (over all seasons)
totalPoints <- 0
totalGoals <- 0
for(id in unique(data$matchID)) {
  score <- data[data$matchID == id,]$score[1]
  points <- data[data$matchID == id,]$pointsWon[1]
  # split the score and add all goals scored
  totalGoals <- totalGoals + sum(as.numeric(unlist(strsplit(score, ' : '))))
  # in case of a tie, each team earns 1 point (2 together) and
  # else it was a win/defeat, thus one team receives 3 points
  if(points == 1) {
    totalPoints <- totalPoints + 2
  } else {
    totalPoints <- totalPoints + 3
  }
  Progressor(which(id == unique(data$matchID)), length(unique(data$matchID)))
}

# Points per goal
pointsPerGoal <- totalPoints / totalGoals

I4 <- function(data, pointsPerGoal) {
  # select players that scored more than 0 goals
  goalScorerDF <- subset(data[, c('name', 'goalScored')], goalScored > 0)
  # aggregate goals per player
  outputDF <- aggregate(goalScored ~ name, sum, data = goalScorerDF)
  # select players with goal = 0 and add to data.frame
  names <- outputDF[, "name"]
  namesOthers <- unique(subset(data, !(name %in% names))[, "name"])
  outputDF <- rbind(outputDF, 
                    data.frame(name = namesOthers, 
                               goalScored = rep(0, length(namesOthers))))
  # points for I4 are the scored gload times points per goal
  outputDF[, "pointsI4"] <- outputDF[, "goalScored"] * pointsPerGoal
  return(outputDF)
}
#example
season2014I4 <- I4(data, pointsPerGoal)
#quick check
if(viewIndices) {
  View(season2014I4[order(season2014I4$pointsI4, decreasing = TRUE), ])
}
#Subindex 5: Assist Index

# Description:
# Analogous to the goals-scored index, each player who
# provides an assist gets pointsPerGoal for that assist.

I5 <- function(data, pointsPerGoal) {
  # select players that had more than 0 assists
  assistDF <- subset(data[, c('name', 'assists')], assists > 0)
  # aggregate goals per player
  outputDF <- aggregate(assists ~ name, sum, data = assistDF)
  # select players with goal = 0 and add to data.frame
  names <- outputDF[, "name"]
  namesOthers <- unique(subset(data, !(name %in% names))[, "name"])
  outputDF <- rbind(outputDF, 
                    data.frame(name = namesOthers, 
                               assists = rep(0, length(namesOthers))))
  # points for I4 are the scored gload times points per goal
  outputDF[, "pointsI5"] <- outputDF[, "assists"] * pointsPerGoal
  return(outputDF)
}
#example
season2014I5 <- I5(data, pointsPerGoal)
#quick check
if(viewIndices) {
  View(season2014I5[order(season2014I5$pointsI5, decreasing = TRUE), ])
}




#Subindex 6: Clean-Sheets Index

# Description:
# The clean-sheet index awards points for not receiving a goal. 
# The points given for a clean sheet are weighted by the players that 
# have the biggest impact on a clean sheet

# To maintain the balance of the overall index, we take
# the total points awarded for clean sheets to be equal
# to the total points for assists.

totalAssists <- sum(data$assists)

totalCleanSheets <- 0
for(ID in unique(data$matchID)) {
  if(as.logical(subset(data, matchID == ID 
                       & pitch == 'home')[1,'cleanSheet'])) {
    totalCleanSheets <- totalCleanSheets + 1
  }
  if(as.logical(subset(data, matchID == ID 
                       & pitch == 'away')[1,'cleanSheet'])) {
    totalCleanSheets <- totalCleanSheets + 1
  }
  # monitor progress
  Progressor(which(ID == unique(data$matchID)), length(unique(data$matchID)))
}

pointsPerCleanSheet <- (pointsPerGoal * totalAssists) / totalCleanSheets

# We now need to divide these
# points among the entire team that achieved the clean
# sheet; thus, the points for the clean sheet are not
# awarded to a single player.

defensiveActions <- c('shotBlocked', 
                      "clearanceTotal", 
                      'tackleWonTotal',
                      'interceptionAll',
                      'saves')

# the extended version not according to the article but
# with additional defensive actions that are available from the data
# the offsides given could be also considered but should be distributed
# evenly amoung the clean sheet team
defensiveActionsExtended <- c('shotBlocked', 
                          "clearanceTotal", 
                          'tackleWonTotal',
                          'interceptionAll',
                          'saves', 
                          'dispossessed',
                          "duelAerialWon")

# different player positions divided into defense, midfield and attack
defense <- c('DC', 'DR', 'DL', "DMC", 'DMR', 'DML')
midfield <- c('MR', 'MC', 'ML','AMC', 'AMR', 'AML')
attack <- c('FW', "FWR", 'FWL')

# compute weights for clean sheet
totalGoali <- 0
totalDefense <- 0
totalMidfield <- 0
totalAttack <- 0
totalSub <- 0

# substitute player are not taken into account because
# there is no information on which position they took oven
# when they entered the game (this does not matter for the clena sheet weights)

for(i in 1:dim(data)[1]) {
  player <- data[i,]
  playerActions <- 0
  for(stat in defensiveActions) {
    playerActions <- playerActions + as.numeric(player[, stat])
  }
  if(player$position == 'GK') {
    totalGoali <- totalGoali + playerActions
  } else if (player$position %in% defense) {
    totalDefense <- totalDefense + playerActions
  } else if (player$position %in% midfield) {
    totalMidfield <- totalMidfield + playerActions
  } else if (player$position %in% attack) {
    totalAttack <- totalAttack + playerActions
  } else {
    totalSub <- totalSub + playerActions
  }
  Progressor(i, dim(data)[1])
}

# The proportion of total defensive actions made
# per position (based on four defenders, four midfielders, two strikers
# and one goal keeper per team);

# when we calculate the distribution of positions among player, we get
# a value of 0.99 for goali, 5.17 for defense, 3.41 for mid and 1.43 for striker
# for an improved version of the index, this allocation numbers can be used

totalWeight <- (totalGoali + totalDefense + totalMidfield + totalAttack)

weightGK <- totalGoali / totalWeight
weightDef <- totalDefense / 4 / totalWeight
weightMid <-  totalMidfield / 4 / totalWeight
weightAtt <- totalAttack / 2 / totalWeight

# allocation according to real distribution
# weightGK <- totalGoali / totalWeight / 0.99
# weightDef <- totalDefense / totalWeight / 5.17
# weightMid <-  totalMidfield / totalWeight / 3.41
# weightAtt <- totalAttack / totalWeight / 1.43

# calculate probability of sub to play on a certain position

# goalis and substitutes are not taken into account because
# goalis get almost never subsituted
positions <- table(data$position)
positions <- positions[!(names(positions) %in% c('GK', 'Sub'))]
playerProp <- prop.table(positions)

defProp <- sum(playerProp[names(playerProp) %in% defense])
midProp <- sum(playerProp[names(playerProp) %in% midfield])
attProp <- sum(playerProp[names(playerProp) %in% attack])

# put all weights and proportions together to insert them into I6 function
weights <- list(weightGK = weightGK, 
                weightDef = weightDef, 
                weightMid = weightMid,
                weightAtt = weightAtt,
                defProp = defProp,
                midProp = midProp,
                attProp = attProp)

I6 <- function(data, pointsPerCleanSheet, weights) {
  with(weights, {
    # every player receives zero points at beginning
    outputDF <- data.frame(name = unique(data$name), pointsI6 = 0)
    for(ID in unique(data$matchID)) {
      homeTeam <- subset(data, matchID == ID 
                         & pitch == 'home')
      awayTeam <- subset(data, matchID == ID 
                         & pitch == 'away')
      # players that should receive points put into receivePoints df
      receivePoints <- data.frame()
      if(as.logical(homeTeam[1,'cleanSheet'])) {
          receivePoints <- rbind(receivePoints, homeTeam)
      }
      if(as.logical(awayTeam[1,'cleanSheet'])) {
        receivePoints <- rbind(receivePoints, awayTeam)
      }
      # if there are players that should receive points,
      # allocate points according to weights
      if(nrow(receivePoints) > 0) {
        for(i in 1:dim(receivePoints)[1]) {
          player <- receivePoints[i,]
          if(player$position == 'GK') {
            points <- weightGK * pointsPerCleanSheet
          } else if (player$position %in% defense) {
            points <- weightDef * pointsPerCleanSheet
          } else if (player$position %in% midfield) {
            points <- weightMid * pointsPerCleanSheet
          } else if (player$position %in% attack) {
            points <- weightAtt * pointsPerCleanSheet
          } else {
            # else if player is substitute, we draw 
            # the sub position from distribution of positions
            points <- sample(c(weightDef, 
                               weightMid, 
                               weightAtt),
                             size = 1,
                             prob = c(defProp,
                                      midProp,
                                      attProp)) * pointsPerCleanSheet
          }
          # update points of player
          nameIndex <- which(outputDF$name == player$name)
          outputDF$pointsI6[nameIndex] <- (outputDF$pointsI6[nameIndex] 
                                            + points)
        }
      }
      # monitor progress
      Progressor(which(ID == unique(data$matchID)), length(unique(data$matchID)))
    }
    return(outputDF)
  })
}

#example
season2014I6 <- I6(data, pointsPerCleanSheet, weights)
#quick check
if(viewIndices) {
  View(season2014I6[order(season2014I6$pointsI6, decreasing = TRUE), ])
}



