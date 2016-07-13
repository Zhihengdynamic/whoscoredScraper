# Master Thesis
# Jonathan Klaiber
# created 05.03.2016
# last modified: 05.03.2016
set.seed(123)


# View indices
viewIndices <- FALSE

# get path to repository
path <- unlist(read.table('repPath.txt', stringsAsFactors = FALSE))

#internal functions
source(paste0(path, '/Progressor.R'))
source(paste0(path, '/derivativeFunction.R'))

# load data from repository
data <- read.csv(file.path(path, 'player_stats_complete_validated.csv'), 
                 encoding = 'UTF-8', 
                 stringsAsFactors = FALSE)
# load data of current season
# curData <- read.csv(file.path(path, 'player_stats_15_16_validated.csv'), 
#                  encoding = 'UTF-8', 
#                  stringsAsFactors = FALSE)

#data <- subset(data, season == '2014-2015')

data$saves <- as.numeric(data$saves)
# data$yellowCard <- as.logical(data$yellowCard)
# data$redCard <- as.logical(data$redCard)

curData <- subset(data, season == '2015-2016')
modelData <- subset(data, season != '2015-2016')

data <- curData
#data <- subset(data, season == '2014-2015')

# Develop the different sub indices

#Subindex 1: Modelling Match Outcome

matches <- unique(modelData$matchID)


# prob of home goal given shot by home team (shot effectiveness)
# in PPI this is constant per team in season 
# for a extended (beter) version, it should be also dependent on home/away effect
teams <- unique(modelData$team)

# data should contain only one season
shotEffectDF <- data.frame()
for(team in teams) {
  goalsHome <- sum(modelData$goalScored[modelData$team == team 
                                        & modelData$pitch == 'home'])
  goalsAway <- sum(modelData$goalScored[modelData$team == team 
                                        & modelData$pitch == 'away'])
  shotsHome <- sum(modelData$shotsTotal[modelData$team == team 
                                        & modelData$pitch == 'home'])
  shotsAway <- sum(modelData$shotsTotal[modelData$team == team 
                                        & modelData$pitch == 'away'])
  shotEffect <- (goalsHome + goalsAway) / (shotsHome + shotsAway)
  shotEffectDF <- rbind(shotEffectDF, data.frame(team = team, 
                                                 shotEffect = shotEffect,
                                                 goalsHome = goalsHome,
                                                 goalsAway = goalsAway,
                                                 shotsHome = shotsHome,
                                                 shotsAway = shotsAway,
                                                 stringsAsFactors = FALSE))
}
#View(shotEffectDF)

ph <- pa <-  with(shotEffectDF, (mean(goalsHome) + mean(goalsAway)) / 
                (mean(shotsHome) + mean(shotsAway)))



aggregatedDF <- data.frame()
aggregatedDFex <- data.frame()
for(match in matches) {
  matchDat <- subset(modelData, matchID == match)
  
  teams <- paste0(c(matchDat$team[matchDat$pitch == 'home'][1], 
                    matchDat$team[matchDat$pitch == 'away'][1]),
                  collapse = ' - ')
  hShots <- sum(matchDat$shotsTotal[matchDat$pitch == 'home'])
  aShots <- sum(matchDat$shotsTotal[matchDat$pitch == 'away'])
  hCross <- sum(matchDat$passCrossTotal[matchDat$pitch == 'home'])
  aCross <- sum(matchDat$passCrossTotal[matchDat$pitch == 'away'])
  hDribbels <- sum(matchDat$dribbleWon[matchDat$pitch == 'home'])
  aDribbels <- sum(matchDat$dribbleWon[matchDat$pitch == 'away'])
  hPass <- sum(matchDat$totalPasses[matchDat$pitch == 'home'])
  aPass <- sum(matchDat$totalPasses[matchDat$pitch == 'away'])
  hInterc <- sum(matchDat$interceptionAll[matchDat$pitch == 'home'])
  aInterc <- sum(matchDat$interceptionAll[matchDat$pitch == 'away'])
  hYellow <- sum( matchDat$yellowCard[matchDat$pitch == 'home'])
  aYellow <- sum( matchDat$yellowCard[matchDat$pitch == 'away'])
  hRed <- sum( matchDat$redCard[matchDat$pitch == 'home'])
  aRed <- sum( matchDat$redCard[matchDat$pitch == 'away'])
  # takles won should be replaced by tackles won/ tackles lost ratio
  hTackle <- sum( matchDat$tackleWonTotal[matchDat$pitch == 'home'])
  aTackle <- sum( matchDat$tackleWonTotal[matchDat$pitch == 'away'])
  hCleared <- sum( matchDat$clearanceTotal[matchDat$pitch == 'home'])
  aCleared <- sum( matchDat$clearanceTotal[matchDat$pitch == 'away'])
  # extended team stats
  hBigError <- sum( matchDat$bigError[matchDat$pitch == 'home'])
  aBigError <- sum( matchDat$bigError[matchDat$pitch == 'away'])
  hDispo <- sum( matchDat$dispossessed[matchDat$pitch == 'home'])
  aDispo <- sum( matchDat$dispossessed[matchDat$pitch == 'away'])
  hDuelWon <- sum( matchDat$duelAerialWon[matchDat$pitch == 'home'])
  aDuelWon <- sum( matchDat$duelAerialWon[matchDat$pitch == 'away'])  
  hKeyPass <- sum( matchDat$keyPassTotal[matchDat$pitch == 'home'])
  aKeyPass <- sum( matchDat$keyPassTotal[matchDat$pitch == 'away']) 
  hPassLong <- sum( matchDat$passLongBallTotal[matchDat$pitch == 'home'])
  aPassLong <- sum( matchDat$passLongBallTotal[matchDat$pitch == 'away'])
  hPassThrough <- sum( matchDat$passThroughBallTotal[matchDat$pitch == 'home'])
  aPassThrough <- sum( matchDat$passThroughBallTotal[matchDat$pitch == 'away']) 
  hTouches <- sum( matchDat$touches[matchDat$pitch == 'home'])
  aTouches <- sum( matchDat$touches[matchDat$pitch == 'away'])
  hTurnover <- sum( matchDat$turnover[matchDat$pitch == 'home'])
  aTurnover <- sum( matchDat$turnover[matchDat$pitch == 'away'])
  hSaves <- sum( matchDat$saves[matchDat$pitch == 'home'])
  aSaves <- sum( matchDat$saves[matchDat$pitch == 'away'])
  hOffTarget <- (sum( matchDat$shotsTotal[matchDat$pitch == 'home'])
                 - sum( matchDat$shotOnTarget[matchDat$pitch == 'home']))
  aOffTarget <- (sum( matchDat$shotsTotal[matchDat$pitch == 'away'])
                 - sum( matchDat$shotOnTarget[matchDat$pitch == 'away']))
  
  matchDF <- data.frame(matchID = match,
                        teams = teams,
                        hShots = hShots,
                        aShots = aShots,
                        hCross = hCross,
                        aCross = aCross,
                        hDribbels = hDribbels,
                        aDribbels = aDribbels,
                        hPass = hPass,
                        aPass = aPass,
                        hInterc = hInterc,
                        aInterc = aInterc,
                        hYellow = hYellow,
                        aYellow = aYellow,
                        hRed = hRed,
                        aRed = aRed,
                        hTackle = hTackle,
                        aTackle = aTackle,
                        hCleared = hCleared,
                        aCleared = aCleared,
                        hSaves = hSaves,
                        aSaves = aSaves,
                        hOffTarget = hOffTarget,
                        aOffTarget = aOffTarget)
  
  matchDFex <- cbind(matchDF, data.frame(hBigError = hBigError,
                                         aBigError = aBigError,
                                         hDispo = hDispo,
                                         aDispo = aDispo,
                                         hDuelWon = hDuelWon,
                                         aDuelWon = aDuelWon,
                                         hKeyPass = hKeyPass,
                                         aKeyPass = aKeyPass,
                                         hPassLong = hPassLong,
                                         aPassLong = aPassLong,
                                         hPassThrough = hPassThrough,
                                         aPassThrough = aPassThrough,
                                         hTouches = hTouches,
                                         aTouches = aTouches,
                                         hTurnover = hTurnover,
                                         aTurnover = aTurnover))

  aggregatedDF <- rbind(aggregatedDF, matchDF)
  aggregatedDFex <- rbind(aggregatedDFex, matchDFex)
  
  # monitor progress
  Progressor(which(match == matches), length(matches))      
}
  
#View(aggregatedDF)

# check correlation
# get panel.cor function

source(file.path(path, 'helperFunctions/panel.cor.R'))

# inspecting scatter matrix and correlations
# pairs(aggregatedDF[, c(
#   'hShots', 'hCross',
#   'hDribbels', 'hPass',
#   'aInterc', 'aYellow',
#   'aRed', 'aTackle',
#   'aCleared'
# )], upper.panel = panel.cor)


# expected shots as OLS
expHs <- lm(hShots ~ hCross + 
            hDribbels + 
            hPass + 
            aInterc +
            aYellow +
            aRed +
            aTackle +
            aCleared,
          data = aggregatedDF)
summary(expHs)

# expected shots as OLS
expAs <- lm(aShots ~ aCross + 
              aDribbels + 
              aPass + 
              hInterc +
              hYellow +
              hRed +
              hTackle +
              hCleared, 
            data = aggregatedDF)
summary(expAs)




# cannot be in function because of global variables
#I1
matches <- unique(data$matchID)
outputDF <- data.frame()
measureName <- c('passCrossTotal', 
                 'dribbleWon', 
                 'totalPasses', 
                 'interceptionAll',
                 'yellowCard',
                 'redCard',
                 'tackleWonTotal',
                 'clearanceTotal')
varName <- c('Cross', 'Dribbel', 'Pass', 'Inter',
             'Yellow', 'Red', 'Tackle', 'Cleared')
# link the measure to the variable name
measuresKey <- data.frame(measure = measureName, 
                          var = varName, 
                          stringsAsFactors = FALSE)
perIndex <- which(colnames(data) %in% measureName)

# p to monitor progress
p <- 1
for(curMatchID in matches) {
  matchDF <- subset(data, matchID == curMatchID)
  # set all measures to their match and team within match specific values
  for(matchPitch in c('home', 'away')) {
    pitch <- ifelse(matchPitch == 'home', 'h', 'a')
    # loop to both teams to create the team specific values
    teamDF <- subset(matchDF, pitch == matchPitch)
    for(measure in measureName) {
      varName <- paste0(pitch, measuresKey$var[measuresKey$measure == measure])
      assign(varName, 
             sum(as.numeric(eval(parse(text=paste("teamDF$", measure ))))))
    }
  }
  # now loop through all players to compute their score
  matchOutputDF <- data.frame()
  for(i in 1:nrow(matchDF)) {
    pitch <- matchDF[i, "pitch"]
    pLetter <- strsplit(pitch, split = '')[[1]][1]
    player <- matchDF[i, perIndex]
    playerPoints <- 0
    for(measure in c('passCrossTotal', 'dribbleWon', 'totalPasses')) {
      varName <- paste0(pLetter,
                        measuresKey$var[measuresKey$measure == measure])
      # save old value
      saveValue <- get(varName)
      # change to player value
      assign(varName, as.numeric(player[measure]))
      # compute points for player
      playerPoints <- playerPoints + (player[measure] 
                                      * derivativeFunction(varName, path))
      # set value back to team specific
      assign(varName, saveValue)
    }
    
#     # shots on and shots off target 
#     onTarget <- matchDF[i, 'shotOnTarget']
#     shotTotal <- matchDF[i, 'shotsTotal']
#     offTarget <- shotTotal - onTarget
#     
#     playerPoints <- playerPoints - offTarget
    
    playerDF <- cbind(name = matchDF[i, 'name'], 
                      points =  playerPoints, player)
    matchOutputDF <- rbind(matchOutputDF, playerDF)
  }
  colnames(matchOutputDF)[2] <- 'pointsI1'

  
  for(j in 1:dim(matchOutputDF)[1]) {
    if(!(matchOutputDF$name[j] %in% outputDF$name)) {
      # make new entry in outputDF if player does not exist already or ...
      # get rid of factor levels
      matchOutputDF$name <- unlist(lapply(matchOutputDF$name, as.character))
      outputDF <- rbind(outputDF, matchOutputDF[j,])
    } else {
      # update points of player
      nameIndex <- which(outputDF$name == matchOutputDF$name[j])
      outputDF[nameIndex,-1] <- (outputDF[nameIndex, -1] 
                                       + matchOutputDF[j, -1])
    }
  }
  Progressor(p, length(matches))
  p <- p + 1
}
# rescale the points awarded for each contribution
# so that the total points over all players and games in a 
# season is a season is equal to the total league points in the final
# table.
# total league points in the final table
totalPoints <- 0
for(curMatchID in matches) {
  if(data$result[data$matchID == curMatchID][1] == 'win' |
     data$result[data$matchID == curMatchID][1] == 'defeat') {
    totalPoints <- totalPoints + 3
  } else {
    totalPoints <- totalPoints + 2
  }
}
rescaleFactor <- totalPoints / sum(outputDF$pointsI1)
# rescale points
outputDF$pointsI1 <- outputDF$pointsI1 * rescaleFactor



#example
season2015I1 <- outputDF
#quick check
if(viewIndices) {
  View(season2015I1[order(season2015I1$pointsI1, decreasing = TRUE), ])
}


# not many goalkeeper seem to be in top 30 
# off target shots have to be incorporated
# saves?



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
      for(i in 1:dim(subset(currentData, pitch == loc))[1]) {
        # get player name
        name <- subset(currentData, pitch == loc)$name[i]
        # get player ratio
        ratio <- (subset(currentData, pitch == loc)$playedMinutes[i] 
                        / totalMinutes)
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
season2015I2 <- I2(data)
#quick check
if(viewIndices) {
  View(season2015I2[order(season2015I2$pointsI2, decreasing = TRUE), ])
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
      
      for(i in 1:dim(subset(currentData, pitch == loc))[1]) {
        # get player name
        name <- subset(currentData, pitch == loc)$name[i]
        # get player ratio
        minutes <- subset(currentData, pitch == loc)$playedMinutes[i]
        # current team
        team <- subset(currentData, pitch == loc)$team[i]
        # ratio of number of minutes played by the player to total
        # number of minutes played by the entire team, multiplyed by
        # gamePointAverage
        matchPoints <- (minutes / totalMinutes) * gamePointAverage
        
        matchDF <- rbind(matchDF, data.frame(name = name, 
                                             minutes = minutes,
                                             pointsI3 = matchPoints,
                                             team = team,
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
        outputDF$pointsI3[nameIndex] <- (outputDF$pointsI3[nameIndex] 
                                        + matchDF$pointsI3[j])
      }
    }
    # montiors progress
    Progressor(p, length(matches))
    p <- p + 1
  }
  return(outputDF)
}

#example
season2015I3 <- I3(data, gamePointAverage)
#quick check
if(viewIndices) {
  View(season2015I3[order(season2015I3$pointsI3, decreasing = TRUE), ])
}

#Subindex 4: Goal-Scoring Index

# Description:
# The points awarded to a player in a
# match for goals, I4, is then simply the points per goal
# multiplied by the number of goals.

# compute points per goal (over all seasons)
totalPoints <- 0
totalGoals <- 0
for(id in unique(modelData$matchID)) {
  score <- modelData [modelData$matchID == id,]$score[1]
  points <- modelData [modelData$matchID == id,]$pointsWon[1]
  # split the score and add all goals scored
  totalGoals <- totalGoals + sum(as.numeric(unlist(strsplit(score, ' : '))))
  # in case of a tie, each team earns 1 point (2 together) and
  # else it was a win/defeat, thus one team receives 3 points
  if(points == 1) {
    totalPoints <- totalPoints + 2
  } else {
    totalPoints <- totalPoints + 3
  }
  Progressor(which(id == unique(modelData$matchID)), 
             length(unique(modelData$matchID)))
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
season2015I4 <- I4(data, pointsPerGoal)
#quick check
if(viewIndices) {
  View(season2015I4[order(season2015I4$pointsI4, decreasing = TRUE), ])
}
#Subindex 5: Assist Index

# Description:
# Analogous to the goals-scored index, each player who
# provides an assist gets pointsPerGoal for that assist.

I5 <- function(data, pointsPerGoal) {
  # select players that had more than 0 assists
  assistDF <- subset(data[, c('name', 'assists')])
  # aggregate assists per player
  outputDF <- aggregate(assists ~ name, sum, data = assistDF)
  # select players with asist = 0 and add to data.frame
  names <- outputDF[, "name"]
  namesOthers <- unique(subset(data, !(name %in% names))[, "name"])
  outputDF <- rbind(outputDF, 
                    data.frame(name = namesOthers, 
                               assists = rep(0, length(namesOthers))))
  # correct for assists that have aparently not counted
  # this is done in comparison with the whoscored.com assist table
  
  # two more for mkhitaryan
  outputDF$assists[outputDF$name == 'Henrikh Mkhitaryan'] <- 15
  # one more for junuzovic
  outputDF$assists[outputDF$name == 'Zlatko Junuzovic'] <- 10
  # one more for samperio
  outputDF$assists[outputDF$name == 'Jairo Samperio'] <- 5
  # one more for thomas müller
  outputDF$assists[outputDF$name == 'Thomas Müller'] <- 5
  # one more for ramos
  outputDF$assists[outputDF$name == 'Adrián Ramos'] <- 4
  # two more for danny da costa
  outputDF$assists[outputDF$name == 'Danny da Costa'] <- 4
  # one more for wagner
  outputDF$assists[outputDF$name == 'Sandro Wagner'] <- 4
  # one more for kohr
  outputDF$assists[outputDF$name == 'Dominik Kohr'] <- 3
  # one more for huntelaar
  outputDF$assists[outputDF$name == 'Klaas-Jan Huntelaar'] <- 3
  # one more for kies
  outputDF$assists[outputDF$name == 'Stefan Kießling'] <- 3
  # one more for Rafinha
  outputDF$assists[outputDF$name == 'Rafinha'] <- 3
  # one more for garcia
  outputDF$assists[outputDF$name == 'Santiago García'] <- 3
  # one more for morales
  outputDF$assists[outputDF$name == 'Alfredo Morales'] <- 2
  # one more for cohen
  outputDF$assists[outputDF$name == 'Almog Cohen'] <- 2
  # two more for ujah
  outputDF$assists[outputDF$name == 'Anthony Ujah'] <- 2
  # one more for gustavo
  outputDF$assists[outputDF$name == 'Luiz Gustavo'] <- 2
  # one more for arnold
  outputDF$assists[outputDF$name == 'Maximilian Arnold'] <- 2
  
  
  # points for I4 are the scored gload times points per goal
  outputDF[, "pointsI5"] <- outputDF[, "assists"] * pointsPerGoal
  return(outputDF)
}
#example
season2015I5 <- I5(data, pointsPerGoal)
#quick check
if(viewIndices) {
  View(season2015I5[order(season2015I5$pointsI5, decreasing = TRUE), ])
}




#Subindex 6: Clean-Sheets Index

# Description:
# The clean-sheet index awards points for not receiving a goal. 
# The points given for a clean sheet are weighted by the players that 
# have the biggest impact on a clean sheet

# To maintain the balance of the overall index, we take
# the total points awarded for clean sheets to be equal
# to the total points for assists.

totalAssists <- sum(season2015I5$assists)

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

positions <- table(data$position)
positions <- positions[!(names(positions) %in% c( 'Sub'))]
positionProp <- prop.table(positions)
defPosProp <- sum(positionProp[names(positionProp) %in% defense])
midPosProp <- sum(positionProp[names(positionProp) %in% midfield])
attPosProp <- sum(positionProp[names(positionProp) %in% attack])

sum(c(defPosProp, midPosProp, attPosProp))

nrPlayersDef <- 4
#nrPlayersDef <- defPosProp * 11
nrPlayersMid <- 4
#nrPlayersMid <- midPosProp * 11
nrPlayersFor <- 2
#nrPlayersFor <- attPosProp * 11

totalWeight <- (totalGoali 
                + (totalDefense / nrPlayersDef) 
                + (totalMidfield / nrPlayersMid) 
                + (totalAttack / nrPlayersFor))

weightGK <- totalGoali / totalWeight
weightDef <- (totalDefense / nrPlayersDef) / totalWeight / nrPlayersDef
weightMid <-  (totalMidfield / nrPlayersMid) / totalWeight / nrPlayersMid
weightAtt <- (totalAttack / nrPlayersFor) / totalWeight / nrPlayersFor

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
season2015I6 <- I6(data, pointsPerCleanSheet, weights)
#quick check
if(viewIndices) {
  View(season2015I6[order(season2015I6$pointsI6, decreasing = TRUE), ])
}



# FINAL INDEX
# get the players position that he played the most
players <- unique(data$name)
playerPos <- numeric()
for(player in players) {
  # get all positions that the player played on, except substitute
  playerDat <- subset(data[, c('name', 'position')], 
                      name == player & position != 'Sub')
  # if he was only subsitute, then that is his position
  if(nrow(playerDat) == 0) {
    mostPlayedPos <- 'Sub'
  } else {
    mostPlayedPos <- labels(which.max(table(playerDat$position)))
  }
  playerPos <- rbind(playerPos, c(player, mostPlayedPos))
}
playerPos <- data.frame(playerPos, stringsAsFactors = FALSE)
colnames(playerPos) <- c('name', 'position')

# 
# merge all subindex datasets
finalDF <- Reduce(function(...) merge(..., 
                                       by = c("name")), 
                   list(season2015I1,
                        season2015I2,
                        season2015I3,
                        season2015I4,
                        season2015I5,
                        season2015I6,
                        playerPos))


finalDF <- finalDF[, c('name', 'team', 'position',
                       'pointsI1',
                       'pointsI2',
                       'pointsI3',
                       'pointsI4',
                       'pointsI5',
                       'pointsI6')]

# weighted average of all subindexes forms the final index score
# I1 match contribution
# I2 winning performance
# I3 match appearances
# I4 goals scored
# I5 assists
# I6 clean sheets
finalDF$PPI <- round(100 * ((0.25 * finalDF$pointsI1) +
                            (0.375 * finalDF$pointsI2) +
                            (0.125 * finalDF$pointsI3) +
                            (0.125 * finalDF$pointsI4) +
                            (0.0625 * finalDF$pointsI5) +
                            (0.0625 * finalDF$pointsI6)))
# finalDF$PPI2 <- round(100 * ((0.25 * finalDF$pointsI1) +
#                               (0.375 * finalDF$pointsI2) +
#                               (0.125 * finalDF$pointsI3) +
#                               (0.09375 * finalDF$pointsI4) +
#                               (0.0625 * finalDF$pointsI5) +
#                               (0.09375 * finalDF$pointsI6)))
finalDF <- finalDF[order(finalDF$PPI, decreasing = TRUE),]
View(finalDF)

# calculate the number of games that were rated
for(i in 1:nrow(finalDF)) {
  playerName <- finalDF$name[i]
  # calculate how many ratings the player received
  nrRatings <- nrow(subset(data, name == playerName & rating != '-'))
  finalDF$gamesRated[i] <- nrRatings
}


         
save(finalDF, file = paste0(path, '/finalDF.RData'))
