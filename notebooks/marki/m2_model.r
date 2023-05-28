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









