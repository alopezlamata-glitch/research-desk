# Replicación cruzada de code/analysis/lp.py con fixest: mismas LP (h = 0, 6, 12, 18, 24), 6 retardos de
# (dip, dcpi, dur, spread, shock) y varianza sándwich de White, calculada con la matriz de diseño de fixest.
# Uso (desde la raíz del repo): Rscript papers/p07-credit/code/replication_r/lp.R
suppressPackageStartupMessages({ library(fixest); library(arrow) })

paper <- "papers/p07-credit"
HORIZONS <- c(0, 6, 12, 18, 24)
LAGS <- 6
LAGGED <- c("dip", "dcpi", "dur", "spread", "shock")
panel <- as.data.frame(read_parquet(file.path(paper, "data/clean/panel.parquet")))

lagk <- function(x, k) c(rep(NA, k), x[seq_len(length(x) - k)])
lead <- function(x, h) if (h == 0) x else c(x[-(1:h)], rep(NA, h))

rows <- list()
for (h in HORIZONS) {
  d <- data.frame(y = lead(panel$lip, h) - lagk(panel$lip, 1), shock = panel$shock,
                  shock_x_credit = panel$shock * lagk(panel$credit, 1))
  for (v in LAGGED) for (j in seq_len(LAGS)) d[[paste0(v, "_l", j)]] <- lagk(panel[[v]], j)
  d <- na.omit(d)
  m <- feols(as.formula(paste("y ~", paste(setdiff(names(d), "y"), collapse = " + "))), data = d)
  X <- model.matrix(m)
  bread <- solve(crossprod(X))
  u <- resid(m)
  se <- sqrt(diag(bread %*% crossprod(X * u) %*% bread))
  for (term in c("shock", "shock_x_credit")) {
    rows[[length(rows) + 1]] <- data.frame(spec_id = paste0("lp_h", h), term = term,
                                           estimate = unname(coef(m)[term]), std_error = unname(se[term]))
  }
}
out <- do.call(rbind, rows)
write.csv(out, file.path(paper, "output/estimates_r.csv"), row.names = FALSE, quote = FALSE)
print(out)
