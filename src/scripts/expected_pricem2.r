library(arrow)
library(lme4)

input_path <- "../../data/apart_df.parquet"

apart_df <- read_parquet(input_path)

pl_df <- na.omit(apart_df[, c("price_m2", "living_area", "namedut",
                              "listing_id")])
pl_df$log_area <- log(pl_df$living_area)
pl_df <- pl_df[order(pl_df$living_area), ]

glmer_int_poly <- glmer(price_m2 ~ poly(log_area, 4) +
                             (1 | namedut), data=pl_df,
                        family=gaussian(link="log"))


## Living area each 5 meters, then log
living_area <- seq(1, 1000, 5)

unique_municipalities <- unique(pl_df$namedut)

n_municipalities <- length(unique_municipalities)

rep_living_area <- rep(living_area, n_municipalities)

rep_municipalities <- rep(unique_municipalities, each=length(living_area))

imp_df <- data.frame(living_area = rep_living_area, namedut = rep_municipalities)
imp_df$log_area <- log(imp_df$living_area)

imp_df$y_hat <- predict(glmer_int_poly, newdata = imp_df, type= "response")
imp_df$y_hat <- round(imp_df$y_hat, 3)

## Print head of output dataframe
print(head(imp_df, n=3L))

export_path <- "../../data/pm2_df.parquet"

write_parquet(imp_df, export_path)

output_message <- paste("Exported price_m2 predictions to:",
                        R.utils::getAbsolutePath(export_path))

print(output_message)


