# Réplica en R de s1r_lin, s1r_liq y s1r_liq_nov (SPEC, «Prerregistro de la etapa 1 rediseñada», prereg_commit 3d6b508; F15).
# Construcción propia del panel, de ȳ, de los regresores y del estado (no reutiliza el código Python). Coeficientes con fixest::feols;
# ee NW(5) de Bartlett en trimestres naturales con residuos HC3 (u_i / (1 − h_ii)), sin corrección N/(N − k), escritos a mano porque
# fixest no combina HC3 con el núcleo HAC. t de N − k g.l.
#
# Uso (desde cualquier carpeta):
#   Rscript papers/p01-liquidity/code/replication_r/s1r_replication.R
#       datos reales (parquet de F7 + CSV de FRED en data/raw); escribe output/estimates_r.csv. NO SE EJECUTA hasta F16: mira la
#       inversión real.
#   Rscript papers/p01-liquidity/code/replication_r/s1r_replication.R panel.csv salida.csv
#       panel dado (quarter, rr_shock, s_lag, in_rr_sample, inv, gdp, defl, ffr); lo usan los tests con datos simulados.

suppressPackageStartupMessages(library(fixest))
args <- commandArgs(trailingOnly = TRUE)
file_arg <- sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value = TRUE))
PAPER <- normalizePath(file.path(dirname(file_arg), "..", ".."))
HZ <- 4:12; SHOCK_LAGS <- 10; SHOCK_LEADS <- 12; CTRL_LAGS <- 2; NW_LAGS <- 5
VOLCKER <- c("1979Q4", "1982Q4")

qid <- function(s) as.integer(substr(s, 1, 4)) * 4L + as.integer(substr(s, 6, 6)) - 1L

if (length(args) == 0) {
  d <- as.data.frame(arrow::read_parquet(file.path(PAPER, "data", "clean", "stage1r_us.parquet")))
  d$quarter <- as.character(d$quarter)
  fred <- function(id) {
    f <- read.csv(file.path(PAPER, "data", "raw", "stage1_us", paste0(id, ".csv")))
    fq <- as.integer(substr(f$observation_date, 1, 4)) * 4L + (as.integer(substr(f$observation_date, 6, 7)) - 1L) %/% 3L
    f[[id]][match(qid(d$quarter), fq)]
  }
  d$inv <- fred("A008RA3Q086SBEA"); d$gdp <- fred("GDPC1"); d$defl <- fred("GDPDEF")
  out_csv <- file.path(PAPER, "output", "estimates_r.csv")
} else {
  d <- read.csv(args[1], stringsAsFactors = FALSE)
  out_csv <- args[2]
}
qn <- qid(d$quarter)
stopifnot(all(diff(qn) == 1L))
TT <- nrow(d)
lagv <- function(x, k) if (k >= 0) c(rep(NA, k), x[seq_len(TT - k)]) else c(x[(1 - k):TT], rep(NA, -k))
na0 <- function(x) { x[is.na(x)] <- 0; x }

# muestras: la de Romer-Romer y sin Volcker (solo se quitan filas)
full <- which(as.logical(d$in_rr_sample) & !is.na(d$s_lag) & !is.na(d$rr_shock))
nov <- full[!(qn[full] >= qid(VOLCKER[1]) & qn[full] <= qid(VOLCKER[2]))]
D <- as.numeric(d$s_lag < median(d$s_lag[full]))  # estado con la mediana de la muestra completa

# ȳ_t y controles
ly <- log(d$inv)
ybar <- Reduce(`+`, lapply(HZ, function(h) 100 * (lagv(ly, -h) - lagv(ly, 1)))) / length(HZ)
ctl <- list(dlinv = c(NA, 100 * diff(ly)), dlgdp = c(NA, 100 * diff(log(d$gdp))), dldefl = c(NA, 100 * diff(log(d$defl))),
            dffr = c(NA, diff(d$ffr)))

regressors <- function(model) {
  e <- d$rr_shock; e0 <- na0(e)
  X <- if (model == "lin") data.frame(b_lin = e) else data.frame(D = D, b_C = D * e, b_U = (1 - D) * e)
  for (j in seq_len(SHOCK_LAGS)) X[[paste0("eps_l", j)]] <- lagv(e0, j)
  for (j in seq_len(SHOCK_LEADS)) X[[paste0("eps_f", j)]] <- lagv(e0, -j)
  for (l in seq_len(CTRL_LAGS)) for (v in names(ctl)) X[[paste0(v, "_l", l)]] <- lagv(ctl[[v]], l)
  X
}

estimate <- function(spec_id, model, rows) {
  X <- regressors(model)[rows, ]
  dd <- cbind(y = ybar[rows], X)
  stopifnot(!anyNA(dd))
  fit <- feols(reformulate(names(X), "y"), data = dd)
  M <- model.matrix(fit)
  stopifnot(ncol(M) == ncol(X) + 1)  # feols no ha quitado ningún regresor por colinealidad
  bread <- solve(crossprod(M))
  u <- resid(fit) / (1 - rowSums((M %*% bread) * M))
  s <- M * u
  q <- qn[rows]
  W <- pmax(1 - abs(outer(q, q, "-")) / (NW_LAGS + 1), 0)  # la matriz va primero: pmax conserva los atributos del primero
  V <- bread %*% t(s) %*% W %*% s %*% bread
  term <- sub("^\\(Intercept\\)$", "const", colnames(M))
  data.frame(spec_id = spec_id, term = term, estimate = unname(coef(fit)[colnames(M)]), std_error = sqrt(diag(V)),
             dof = nrow(M) - ncol(M))
}

res <- rbind(estimate("s1r_lin", "lin", full), estimate("s1r_liq", "liq", full), estimate("s1r_liq_nov", "liq", nov))
res$estimate <- sprintf("%.17g", res$estimate); res$std_error <- sprintf("%.17g", res$std_error)
write.csv(res, out_csv, row.names = FALSE, quote = FALSE)
cat(sprintf("escrito %s (%d filas)\n", out_csv, nrow(res)))
