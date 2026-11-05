# Replicación cruzada de code/analysis/lp.py con fixest: mismas LP h = 0..4 y Newey-West (Bartlett, h + 1 retardos)
# sobre residuos HC3, calculado con la matriz de diseño de fixest.
# Uso (desde la raíz del repo): Rscript papers/p07-credit/code/replication_r/lp.R
suppressPackageStartupMessages({ library(fixest); library(arrow) })

paper <- "papers/p07-credit"
H <- 4
panel <- as.data.frame(read_parquet(file.path(paper, "data/clean/panel.parquet")))

lag1 <- function(x) c(NA, x[-length(x)])
lead <- function(x, h) if (h == 0) x else c(x[-(1:h)], rep(NA, h))

newey_west <- function(X, u, lags) {
  bread <- solve(crossprod(X))
  s <- X * u
  meat <- crossprod(s)
  n <- nrow(s)
  for (l in seq_len(lags)) {
    g <- crossprod(s[(l + 1):n, , drop = FALSE], s[1:(n - l), , drop = FALSE])
    meat <- meat + (1 - l / (lags + 1)) * (g + t(g))
  }
  bread %*% meat %*% bread
}

rows <- list()
for (h in 0:H) {
  d <- data.frame(y = lead(panel$loginv, h) - lag1(panel$loginv), shock = panel$shock,
                  credit_l1 = lag1(panel$credit), dinv_l1 = lag1(panel$dinv), dgdp_l1 = lag1(panel$dgdp),
                  infl_l1 = lag1(panel$infl), fci_l1 = lag1(panel$fci))
  d$shock_x_credit <- d$shock * d$credit_l1
  d <- na.omit(d)
  m <- feols(y ~ shock + shock_x_credit + credit_l1 + dinv_l1 + dgdp_l1 + infl_l1 + fci_l1, data = d)
  X <- model.matrix(m)
  u <- resid(m) / (1 - rowSums((X %*% solve(crossprod(X))) * X))  # residuos HC3
  se <- sqrt(diag(newey_west(X, u, h + 1)))
  for (term in c("shock", "shock_x_credit")) {
    rows[[length(rows) + 1]] <- data.frame(spec_id = paste0("lp_h", h), term = term,
                                           estimate = unname(coef(m)[term]), std_error = unname(se[term]))
  }
}
out <- do.call(rbind, rows)
write.csv(out, file.path(paper, "output/estimates_r.csv"), row.names = FALSE, quote = FALSE)
print(out)
