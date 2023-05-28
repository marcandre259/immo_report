library(data.table)
library(splines)
library(lme4)
library(arrow)

apart_df <- read_parquet("data/apart_df.parquet")

## head(apart_df)
## Drop rows with missing price or living_area
pl_df <- na.omit(apart_df[, c("price_m2", "living_area", "namedut")])
pl_df$log_area = log(pl_df$living_area)
pl_df <- pl_df[order(pl_df$living_area), ]

knots <- quantile(pl_df$log_area, 0.5)
lm_area <- lm(price_m2 ~ bs(log_area, degree=3, knots=knots), data=pl_df)

y_hat <- predict(lm_area)

# Does not give a correct fit at the higher extreme

## Attempt with simpler model (quadratic)
lm_area_poly <- lm(price_m2 ~ poly(log_area, 4), data=pl_df)

y_hat_poly <- predict(lm_area_poly)

## I should only be able to get positive values on price, so let's
## take a log transform of the price
## This last model is also apparently correct in the extremes. 
glm_area_poly <- glm(price_m2 ~ poly(log_area, 4),
                     data=pl_df,
                     family=gaussian(link="log"))

y_hat_glm_poly <- predict(glm_area_poly, type="response")

plot(pl_df$log_area, pl_df$price_m2, col = rgb(0, 0, 0, alpha=0.5))
lines(pl_df$log_area, y_hat, col="red")
lines(pl_df$log_area, y_hat_poly, col="blue")
lines(pl_df$log_area, y_hat_glm_poly, col="green")

## Now I'd like to allow for varying effect depending on the municipality
## (geographic unit)

## glmer_area_poly <- glmer(price_m2 ~ poly(log_area, 4) + (1 +
##                          poly(log_area, 4) | namedut), data=pl_df,
##                          family=gaussian(link="log"))

glmer_area_poly <- glmer(price_m2 ~ poly(log_area, 4) +
                             (1 + log_area | namedut), data=pl_df,
                         family=gaussian(link="log"))

## Check goodness of fit vs fixed model
anova(glmer_area_poly, glm_area_poly)

## I don't think I really need a random effect, per city, I only
## expect the baseline price_m2 to change
glmer_int_poly <- glmer(price_m2 ~ poly(log_area, 4) +
                             (1 | namedut), data=pl_df,
                        family=gaussian(link="log"))

anova(glmer_area_poly, glmer_int_poly)

## Check R2 of the three contending models
r2_check <- function(glmer_mod, outcome) {
    y_hat <- predict(glmer_mod, type="response")
    denom <- mean((outcome - y_hat)^2)
    nom <- var(outcome)
    return(1 - denom/nom)
}

## Big improvement in fit by accounting for municipality
r2_check(glmer_int_poly, pl_df$price_m2)

r2_check(glmer_area_poly, pl_df$price_m2)

r2_check(glm_area_poly, pl_df$price_m2)











