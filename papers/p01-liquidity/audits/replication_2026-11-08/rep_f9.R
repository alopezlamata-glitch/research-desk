# R-F10 · Replicación independiente en R del Monte Carlo de F9 (diseño s1r_*; Referee, 2026-11-08).
# Sin código del autor. Regla dura: la inversión real solo entra como AR(2) univariante de su crecimiento (sin choques), para
# calibrar el ruido; la variable dependiente ȳ y el control Δlog inversión se simulan. No se estima nada con la inversión real.
# Uso (desde la raíz del repo): Rscript papers/p01-liquidity/audits/replication_2026-11-08/rep_f9.R [reps] [seed]
#
# Construcción propia (distinta de f9_power.py): la señal de ȳ_t se calcula con pesos analíticos w(k) por choque
# (k = t − s), no convolucionando el nivel; el ruido de ȳ_t, con sumas acumuladas del crecimiento simulado.

args <- commandArgs(trailingOnly = TRUE)
REPS <- if (length(args)) as.integer(args[1]) else 2000L
SEED <- if (length(args) > 1) as.integer(args[2]) else 20261108L
OMEGA <- 0.146
HZ <- 4:12
BURN <- 40L

d <- as.data.frame(arrow::read_parquet("papers/p01-liquidity/data/clean/stage1r_us.parquet"))
qn <- as.integer(substr(d$quarter, 1, 4)) * 4L + as.integer(substr(d$quarter, 6, 6)) - 1L
stopifnot(all(diff(qn) == 1L))
TT <- nrow(d)
fred <- function(id) {
  f <- read.csv(sprintf("papers/p01-liquidity/data/raw/stage1_us/%s.csv", id))
  fq <- as.integer(substr(f$observation_date, 1, 4)) * 4L + (as.integer(substr(f$observation_date, 6, 7)) - 1L) %/% 3L
  f[[id]][match(qn, fq)]
}
inv <- fred("A008RA3Q086SBEA"); gdp <- fred("GDPC1"); defl <- fred("GDPDEF")
lagv <- function(x, k) if (k >= 0) c(rep(NA, k), x[seq_len(TT - k)]) else c(x[(1 - k):TT], rep(NA, -k))
qid <- function(s) as.integer(substr(s, 1, 4)) * 4L + as.integer(substr(s, 6, 6)) - 1L

# muestras
rr_rows <- which(d$in_rr_sample & !is.na(d$s_lag) & !is.na(d$rr_shock))
volck <- qn >= qid("1979Q4") & qn <= qid("1982Q4")
nov_rows <- rr_rows[!volck[rr_rows]]
lastq <- max(qn[rr_rows])
bs_rows <- which(qn >= qid("1988Q1") & qn <= lastq & !is.na(d$mps_bs23_orth) & !is.na(d$s_lag))
cat(sprintf("N: RR %d, RR_noV %d, BS %d\n", length(rr_rows), length(nov_rows), length(bs_rows)))

state <- function(rows) as.numeric(!is.na(d$s_lag) & d$s_lag < median(d$s_lag[rows]))

# β_ref: −2,5 × m_W × π_h, π_h de ffr_{t+h} − ffr_{t−1} sobre (1, ε_t)
m_W <- mean(pmin(HZ, 10) / 10)
pi_h <- function(shock, rows, h) {
  y <- lagv(d$ffr, -h)[rows] - lagv(d$ffr, 1)[rows]
  coef(lm(y ~ shock[rows]))[[2]]
}
rr <- d$rr_shock; bsx <- d$mps_bs23_orth
bref <- c(RR = -2.5 * m_W * pi_h(rr, rr_rows, 0), BS = -2.5 * m_W * pi_h(bsx, bs_rows, 0))
cat(sprintf("m_W = %.6f\n", m_W))
for (h in 0:4) cat(sprintf("pi(h=%d): RR %.6f  RR_noV %.6f  BS %.6f  -> beta_ref RR %.6f\n", h, pi_h(rr, rr_rows, h),
                           pi_h(rr, nov_rows, h), pi_h(bsx, bs_rows, h), -2.5 * m_W * pi_h(rr, rr_rows, h)))

# ---------------------------------------------------------------- señal de ȳ: pesos analíticos
# 100·log I_t = L_t + Σ_s r(t−s) a_s, r(j) = forma de la IRF (r(j) = 0 si j < 0); a_s = β_{estado(s)} ε_s / mean_h r(h)
# ȳ_t ⊃ Σ_s a_s w(t−s), w(k) = mean_h [r(h + k) − r(k − 1)]
shapes <- list(
  ramp = function(j) ifelse(j < 0, 0, pmin(j, 10) / 10),                          # la de F9 (TT, pico en h = 10, permanente)
  fast = function(j) ifelse(j < 0, 0, pmin(j, 4) / 4),                            # pico en h = 4, permanente
  hump = function(j) ifelse(j < 0, 0, (j / 8) * exp(1 - j / 8)))                  # joroba con pico en h = 8 que revierte
wts <- function(r, kmax = 80) { k <- -12:kmax; setNames(sapply(k, function(kk) mean(r(HZ + kk) - r(kk - 1))), k) }
na0 <- function(x) { x[is.na(x)] <- 0; x }
signal_ybar <- function(a, r) {  # los choques sin dato y fuera del calendario cuentan como 0
  w <- wts(r); k <- as.integer(names(w)); out <- numeric(TT)
  for (i in seq_along(k)) if (abs(w[i]) > 0) out <- out + w[i] * na0(lagv(a, k[i]))
  out
}
signal_dlev <- function(a, r) {  # Δ(Σ_s r(t−s) a_s) = Σ_s a_s [r(t−s) − r(t−s−1)]
  k <- 0:(TT - 1); dr <- r(k) - r(k - 1); out <- numeric(TT)
  for (i in seq_along(k)) if (abs(dr[i]) > 0) { l <- lagv(a, k[i]); l[is.na(l)] <- 0; out <- out + dr[i] * l }
  out
}

# ---------------------------------------------------------------- regresores
dlgdp <- c(NA, 100 * diff(log(gdp))); dldefl <- c(NA, 100 * diff(log(defl))); dffr <- c(NA, diff(d$ffr))
design <- function(eps, D, dlinv, rows, model, spec) {
  # aumi (propuesta del Referee): retardos y adelantos del choque partidos por el estado de su propio trimestre, solo en
  # s1r_liq; s1r_lin no tiene estado y usa los de aum
  if (spec == "aumi" && model == "lin") spec <- "aum"
  e0 <- na0(eps)
  core <- if (model == "lin") cbind(c = 1, b = e0) else cbind(c = 1, D = D, bC = D * e0, bU = (1 - D) * e0)
  ctl <- cbind(lagv(dlinv, 1), lagv(dlinv, 2), lagv(dlgdp, 1), lagv(dlgdp, 2), lagv(dldefl, 1), lagv(dldefl, 2),
               lagv(dffr, 1), lagv(dffr, 2))
  ex <- NULL
  if (spec %in% c("aum", "aumi")) {
    js <- c(1:10, -(1:12))
    if (spec == "aum") ex <- sapply(js, function(j) na0(lagv(e0, j)))
    else ex <- cbind(sapply(js, function(j) na0(lagv(D * e0, j))), sapply(js, function(j) na0(lagv((1 - D) * e0, j))))
  }
  cbind(core, ctl, ex)[rows, , drop = FALSE]
}

# ---------------------------------------------------------------- errores estándar
bartlett <- function(q, L) { dd <- abs(outer(q, q, "-")); pmax(1 - dd / (L + 1), 0) }
ses <- function(y, X, q, Wl) {
  n <- nrow(X); k <- ncol(X)
  # sin ruido y con IRF corta, Δlog inversión retardada es combinación exacta de los retardos del choque: inversa generalizada
  # (el coeficiente de ε_t sigue identificado)
  XtXi <- tryCatch(solve(crossprod(X)), error = function(e) MASS::ginv(crossprod(X))); b <- XtXi %*% crossprod(X, y); u <- as.numeric(y - X %*% b)
  h <- rowSums((X %*% XtXi) * X)
  sand <- function(uu, W) { s <- X * uu; sqrt(pmax(diag(XtXi %*% crossprod(s, W %*% s) %*% XtXi), 0)) }
  out <- list(b = as.numeric(b), dof = n - k,
              NW5_HC3 = sand(u / (1 - h), Wl$L5),
              NW5 = sand(u, Wl$L5),
              NW5_df = sand(u, Wl$L5) * sqrt(n / (n - k)),
              NW12_df = sand(u, Wl$L12) * sqrt(n / (n - k)),
              NW12_HC2 = sand(u / sqrt(1 - h), Wl$L12),
              NW5_HC2 = sand(u / sqrt(1 - h), Wl$L5))
  # EWC (Lazarus-Lewis-Stock-Watson 2018), B = 0,4·T^(2/3), en tiempo natural; t con B g.l.
  Tn <- max(q) - min(q) + 1; B <- floor(0.4 * Tn^(2 / 3))
  ewc <- function(uu) {
    s <- X * uu
    Lam <- sapply(1:B, function(j) colSums(s * sqrt(2 / Tn) * cos(pi * j * (q - min(q) + 0.5) / Tn)))
    sqrt(diag(XtXi %*% (tcrossprod(Lam) / B * Tn) %*% XtXi))
  }
  out$EWC <- ewc(u * sqrt(n / (n - k))); out$EWC_HC3 <- ewc(u / (1 - h)); out$B <- B
  out
}
crit <- function(kind, r) if (startsWith(kind, "EWC")) qt(0.975, r$B) else qt(0.975, r$dof)
KINDS <- c("NW5_HC3", "NW5", "NW5_df", "NW12_df", "NW12_HC2", "NW5_HC2", "EWC", "EWC_HC3")

# ---------------------------------------------------------------- DGP
calib <- function(rows) {  # AR(2) univariante del crecimiento de la inversión en `rows` (sin choques)
  g <- c(NA, 100 * diff(log(inv)))
  f <- lm(g[rows] ~ g[rows - 1] + g[rows - 2])
  list(mu = coef(f)[[1]], p1 = coef(f)[[2]], p2 = coef(f)[[3]], res = residuals(f) - mean(residuals(f)))
}
make_dgp <- function(shock, base_rows, bC, bU, noise = "homo", shape = "ramp") {
  D <- state(base_rows); e0 <- na0(shock); r <- shapes[[shape]]
  a <- (bC * D + bU * (1 - D)) * e0 / mean(r(HZ))
  cal <- calib(base_rows)
  sig <- rep(1, TT)
  if (noise == "het_eps") {
    z <- (e0 / sd(shock[base_rows]))^2
    v <- sapply(seq_len(TT), function(t) mean(z[max(1, t - 12):t]))
    sig <- sqrt((1 + v) / mean((1 + v)[base_rows]))
  }
  list(D = D, e0 = e0, sy = signal_ybar(a, r), sd = signal_dlev(a, r), cal = cal, sig = sig)
}
draw <- function(g, scale = 1) {
  cal <- g$cal; n <- TT + BURN
  e <- scale * sample(cal$res, n, replace = TRUE) * c(rep(1, BURN), g$sig)
  x <- numeric(n); m0 <- cal$mu / (1 - cal$p1 - cal$p2); x[1:2] <- m0
  for (t in 3:n) x[t] <- cal$mu + cal$p1 * x[t - 1] + cal$p2 * x[t - 2] + e[t]
  gr <- x[(BURN + 1):n]
  cs <- cumsum(gr)                                         # L_t (salvo constante)
  yn <- sapply(seq_len(TT), function(t) if (t + 12 > TT || t < 2) NA else mean(cs[t + HZ] - cs[t - 1]))
  list(y = yn + g$sy, dlinv = gr + g$sd)
}

fit_all <- function(g, dr, rows, spec) {
  q <- qn[rows]; Wl <- list(L5 = bartlett(q, 5), L12 = bartlett(q, 12))
  rl <- ses(dr$y[rows], design(g$e0, g$D, dr$dlinv, rows, "lin", spec), q, Wl)
  rq <- ses(dr$y[rows], design(g$e0, g$D, dr$dlinv, rows, "liq", spec), q, Wl)
  list(lin = rl, liq = rq)
}

verdict <- function(f, kind = "NW5_HC3") {
  lin <- f$lin; liq <- f$liq
  gl <- function(r) if (startsWith(kind, "EWC")) r$B else r$dof
  h0 <- lin$b[2] / lin[[kind]][2] < qt(0.05, gl(lin))
  tC <- liq$b[3] / liq[[kind]][3]; dl <- OMEGA * abs(liq$b[4])
  h1 <- if (tC < qt(0.05, gl(liq))) "confirma" else if (tC > qt(0.95, gl(liq))) "refuta_a" else
    if (liq$b[3] - qt(0.95, gl(liq)) * liq[[kind]][3] > -dl) "refuta_b" else "no_concluyente"
  list(h0 = h0, h1 = h1, bC = liq$b[3])
}
tree <- function(vf, vn, variant) {
  if (variant == "V2") return(if (vn$h0) vn$h1 else "h0_falla")
  if (!vf$h0) return("h0_falla")
  if (variant == "V1" || vf$h1 != "confirma") return(vf$h1)
  ok <- if (variant == "V3s") vn$h1 == "confirma" else vn$bC < 0
  if (ok) "confirma" else "no_concluyente"
}

# ---------------------------------------------------------------- 1. valores deterministas: error de diseño sin ruido
cat(sprintf("\nbeta_ref RR = %.6f ; BS = %.6f\n", bref[["RR"]], bref[["BS"]]))
cat("\n## Error de diseño relativo (sin ruido, T = N): (b - beta)/beta_ref\n")
design_err <- function(shock, base_rows, smp, m, spec, shape, bR) {
  g <- make_dgp(shock, base_rows, m * bR, bR, shape = shape)
  dr <- draw(g, scale = 0)
  sapply(names(smp), function(sn) {
    f <- fit_all(g, dr, smp[[sn]], spec)
    c(b_lin = if (m == 1) (f$lin$b[2] - bR) / bR else NA, b_C = (f$liq$b[3] - m * bR) / bR, b_U = (f$liq$b[4] - bR) / bR)
  })
}
smpRR <- list(RR = rr_rows, RR_noV = nov_rows)
for (shape in names(shapes)) for (m in c(1, 0)) for (spec in c("base", "aum", "aumi")) {
  E <- design_err(rr, rr_rows, smpRR, m, spec, shape, bref[["RR"]])
  for (sn in colnames(E)) cat(sprintf("%-5s m=%d %-4s %-6s  b_lin %+.6f  b_C %+.6f  b_U %+.6f\n", shape, m, spec, sn,
                                      E["b_lin", sn], E["b_C", sn], E["b_U", sn]))
}
E <- design_err(bsx, bs_rows, list(BS = bs_rows), 1, "base", "ramp", bref[["BS"]])
cat(sprintf("ramp  m=1 base BS      b_lin %+.6f  b_C %+.6f  b_U %+.6f\n", E[1, 1], E[2, 1], E[3, 1]))

# ---------------------------------------------------------------- 2. diagnósticos de los choques (sin inversión)
cat("\n## Autocorrelación de RR y Ljung-Box (12 retardos)\n")
for (sn in names(smpRR)) {
  x <- rr[smpRR[[sn]]]
  lb <- Box.test(x, lag = 12, type = "Ljung-Box")
  cat(sprintf("%s: rho1..4 = %s ; LB(12) = %.2f, p = %.3f\n", sn,
              paste(sprintf("%.3f", acf(x, 4, plot = FALSE)$acf[2:5]), collapse = " "), lb$statistic, lb$p.value))
}
cat("## ¿Predicen el PIB, el deflactor y el fed funds pasados el choque RR? (F de Wald HC1, 4 retardos)\n")
for (sn in names(smpRR)) {
  rows <- smpRR[[sn]]
  Z <- cbind(sapply(1:4, function(j) lagv(dlgdp, j)), sapply(1:4, function(j) lagv(dldefl, j)), sapply(1:4, function(j) lagv(dffr, j)))[rows, ]
  f <- lm(rr[rows] ~ Z)
  V <- sandwich::vcovHC(f, type = "HC1"); b <- coef(f)[-1]; Vb <- V[-1, -1]
  W <- as.numeric(t(b) %*% solve(Vb, b)) / length(b)
  cat(sprintf("%s: F(%d, %d) = %.2f, p = %.3f\n", sn, length(b), f$df.residual, W, pf(W, length(b), f$df.residual, lower.tail = FALSE)))
}

# ---------------------------------------------------------------- 3. Monte Carlo de los escenarios principales (RR)
run_cell <- function(label, m, c, noise, specs, reps, seed) {
  set.seed(seed)
  bR <- bref[["RR"]]
  g <- make_dgp(rr, rr_rows, m * c * bR, c * bR, noise = noise)
  truth <- c(b_lin = c * bR, b_C = m * c * bR, b_U = c * bR)
  res <- list()
  TREE_KINDS <- c("NW5_HC3", "EWC_HC3")  # el árbol se evalúa con la ee de F9 y con la alternativa del Referee
  for (sp in specs) res[[sp]] <- list(est = array(NA, c(reps, 2, 3, length(KINDS) + 1)),
                                       ver = array(NA_character_, c(reps, 4, 2)), h1 = array(NA, c(reps, 2, 2)))
  for (r in seq_len(reps)) {
    dr <- draw(g)
    for (sp in specs) {
      ff <- fit_all(g, dr, rr_rows, sp); fn <- fit_all(g, dr, nov_rows, sp)
      for (si in 1:2) {
        f <- if (si == 1) ff else fn
        est <- c(f$lin$b[2], f$liq$b[3], f$liq$b[4])
        cov <- sapply(KINDS, function(k) {
          se <- c(f$lin[[k]][2], f$liq[[k]][3], f$liq[[k]][4]); cr <- c(crit(k, f$lin), crit(k, f$liq), crit(k, f$liq))
          abs(est - truth) <= cr * se })
        res[[sp]]$est[r, si, , ] <- cbind(est, cov)
        for (ki in 1:2) res[[sp]]$h1[r, si, ki] <- verdict(f, TREE_KINDS[ki])$h1 == "confirma"
      }
      for (ki in 1:2) {
        vf <- verdict(ff, TREE_KINDS[ki]); vn <- verdict(fn, TREE_KINDS[ki])
        res[[sp]]$ver[r, , ki] <- sapply(c("V1", "V2", "V3s", "V3l"), function(v) tree(vf, vn, v))
      }
    }
  }
  for (sp in specs) {
    R <- res[[sp]]
    cat(sprintf("\n### %s · %s · %s · m=%g c=%g · %d réplicas\n", label, sp, noise, m, c, reps))
    for (si in 1:2) for (ti in 1:3) {
      if (m == 0 && ti == 1) next
      x <- R$est[, si, ti, 1]
      cat(sprintf("  %-6s %-5s sesgo %+.3f  sd %.3f  cobertura %s\n", c("RR", "RR_noV")[si], c("b_lin", "b_C", "b_U")[ti],
                  mean(x) - truth[ti], sd(x), paste(sprintf("%s=%.3f", KINDS, colMeans(R$est[, si, ti, -1, drop = FALSE][, 1, 1, ])), collapse = " ")))
    }
    for (ki in 1:2) {
      cat(sprintf("  [%s] potencia H1 sin condicionar: RR %.3f  RR_noV %.3f\n", TREE_KINDS[ki], mean(R$h1[, 1, ki]), mean(R$h1[, 2, ki])))
      for (vi in 1:4) {
        tb <- table(factor(R$ver[, vi, ki], levels = c("h0_falla", "confirma", "refuta_a", "refuta_b", "no_concluyente"))) / reps
        cat(sprintf("  [%s] %-4s %s\n", TREE_KINDS[ki], c("V1", "V2", "V3s", "V3l")[vi],
                    paste(sprintf("%s %.3f", names(tb), tb), collapse = " · ")))
      }
    }
  }
}
t0 <- Sys.time()
run_cell("A", 1, 1, "homo", c("aum", "base"), REPS, SEED + 1)
run_cell("C", 1, 3, "homo", c("aum", "aumi"), REPS, SEED + 2)
run_cell("D", 0, 3, "homo", c("aum", "aumi"), REPS, SEED + 3)
run_cell("E", 1, 1.76, "homo", "aum", REPS, SEED + 4)
run_cell("F", 1, 1, "het_eps", "aum", REPS, SEED + 5)
run_cell("G", 0, 5, "homo", c("aum", "aumi"), REPS, SEED + 6)
run_cell("H", 1, 0, "homo", "aum", REPS, SEED + 7)       # tamaño con β = 0
run_cell("I", 1, 0, "het_eps", "aum", REPS, SEED + 8)
cat(sprintf("\ntiempo: %.1f min\n", as.numeric(difftime(Sys.time(), t0, units = "mins"))))
