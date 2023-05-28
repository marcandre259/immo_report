library(arrow)
library(lme4)

apart_df <- read_parquet("../../data/apart_df.parquet")

pl_df <- na.omit(apart_df[, c("price_m2", "living_area", "namedut",
                              "listing_id")])
pl_df$log_area <- log(pl_df$living_area)
pl_df <- pl_df[order(pl_df$living_area), ]

glmer_int_poly <- glmer(price_m2 ~ poly(log_area, 4) +
                             (1 | namedut), data=pl_df,
                        family=gaussian(link="log"))

pl_df$y_hat <- predict(glmer_int_poly, type="response")

## write_parquet(pl_df, "")

## Print head of output dataframe
print(head(pl_df, n=3L))

export_path <- "../../data/pm2_df.parquet"

write_parquet(pl_df, export_path)

output_message <- paste("Exported price_m2 predictions to:",
                        R.utils::getAbsolutePath(export_path))

print(output_message)


