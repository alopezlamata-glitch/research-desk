# R-F4 · Replicación independiente en R del Monte Carlo de F4 (Referee, 2026-11-05).
# Sin código del autor ni del script Python de esta carpeta. Regla dura: la inversión real solo entra como serie univariante
# (AR(2) del control Δlog inversión, sin choques) y como control retardado; la variable dependiente se simula.
# Uso (desde la raíz del repo): Rscript papers/p01-liquidity/audits/replication_2026-11-05/rep_f4.R [reps]

args <- commandArgs(trailingOnly = TRUE)
REPS <- if (length(args)) as.integer(args[1]) else 1000L
SEED <- if (length(args) > 1) as.integer(args[2]) else 20261105L
ONLY_M1 <- length(args) > 2 && args[3] == "m1"  # solo el escenario m = 1 (comprobación de discrepancias)
set.seed(SEED)
OMEGA_MIN <- 0.146
BURN <- 40L

d <- as.data.frame(arrow::read_parquet("papers/p01-liquidity/data/clean/stage1_us.parquet"))
qn <- as.integer(substr(d$quarter, 1, 4)) * 4L + as.integer(substr(d$quarter, 6, 6)) - 1L
stopifnot(all(diff(qn) == 1L))  # calendario trimestral contiguo
TT <- nrow(d)
lag <- function(x, k) c(rep(NA, k), x[seq_len(length(x) - k)])

# estado: s_t = log(liq)_t − media de log(liq)_{t−1..t−12}; D_{t−1} = s_{t−1} < mediana muestral
ll <- log(d$liq_broad_debt)
s <- ll - rowMeans(sapply(1:12, function(j) lag(ll, j)))
s_prev <- lag(s, 1)
yr <- function(q) as.integer(substr(q, 1, 4)) * 4L + as.integer(substr(q, 6, 6)) - 1L
inwin <- qn >= yr("1988Q2") & qn <= yr("2023Q4") & !(qn >= yr("2019Q1") & qn <= yr("2021Q4"))
keep <- inwin & d$ffr >= 0.25 & !is.na(d$mps_bs23_orth) & !is.na(s_prev)
pos <- which(keep)
n <- length(pos)
eps_all <- d$mps_bs23_orth
eps <- eps_all[pos]
D_all <- as.numeric(!is.na(s_prev) & s_prev < median(s_prev[pos]))
D <- D_all[pos]
cat(sprintf("N = %d; celdas C-, C+, U-, U+ = %d %d %d %d\n", n, sum(D == 1 & eps < 0), sum(D == 1 & eps > 0),
            sum(D == 0 & eps < 0), sum(D == 0 & eps > 0)))

# AR(2) univariante de 100·Δlog inversión (sin choques)
g_real <- c(NA, 100 * diff(log(d$inv_nonres_q)))
ar <- lm(g_real[pos] ~ g_real[pos - 1] + g_real[pos - 2])
mu <- coef(ar)[[1]]; f1 <- coef(ar)[[2]]; f2 <- coef(ar)[[3]]
res <- residuals(ar)
psi <- as.numeric(stats::filter(c(1, 0, 0, 0, 0), c(f1, f2), method = "recursive"))
kap <- mean(cumsum(psi))
cat(sprintf("AR(2): mu=%.9f phi1=%.9f phi2=%.9f sd(df=n-3)=%.9f kappa=%.9f\n", mu, f1, f2, sqrt(sum(res^2) / (n - 3)), kap))

# π_ffr (HC1) y β_ref
dffr <- d$ffr[pos] - d$ffr[pos - 1]
Xp <- cbind(1, eps)
bp <- solve(crossprod(Xp), crossprod(Xp, dffr)); up <- as.numeric(dffr - Xp %*% bp)
Bp <- solve(crossprod(Xp))
se_p <- sqrt((Bp %*% crossprod(Xp * up) %*% Bp)[2, 2] * n / (n - 2))
bref <- -2.5 * mean((0:4) / 10) * bp[2]
cat(sprintf("pi_ffr=%.9f (ee HC1 %.9f); beta_ref=%.9f\n", bp[2], se_p, bref))

# regresores
oth <- cbind(c(NA, 100 * diff(log(d$gdp_real))), c(NA, 100 * diff(log(d$gdp_deflator))), c(NA, diff(d$y2_mean)), d$ebp)
ep <- pmax(eps, 0); en <- pmin(eps, 0)
Xcore <- cbind(1, D, D * ep, (1 - D) * ep, D * en, (1 - D) * en)
Xoth <- cbind(oth[pos - 1, ], oth[pos - 2, ])
X_of <- function(g) cbind(Xcore, g[pos - 1], g[pos - 2], Xoth)
qd <- qn[pos]
Wnw <- matrix(pmax(0, 1 - abs(outer(qd, qd, "-")) / 6), n, n)  # pmax pierde las dimensiones

Xr <- X_of(g_real)
hr <- rowSums((Xr %*% solve(crossprod(Xr))) * Xr)
cat(sprintf("apalancamiento: max=%.3f media=%.3f\n", max(hr), mean(hr)))
for (j in 3:6) {
  e2 <- Xcore[, j]^2; o <- order(e2, decreasing = TRUE)[1:2]
  cat(sprintf("  col %d: top2 = %.3f (%s)\n", j, sum(e2[o]) / sum(e2), paste(d$quarter[pos[o]], collapse = ", ")))
}

# DGP
e0 <- ifelse(is.na(eps_all), 0, eps_all)
rc <- res - mean(res)
sd_eps <- sd(eps)
hsc <- sqrt(1 + (e0 / sd_eps)^2); hsc <- hsc / sqrt(mean(hsc[pos]^2))

sim_g <- function(bC, bU, sigma = 1, hetero = FALSE) {
  b <- ifelse(e0 > 0, D_all * bC[1] + (1 - D_all) * bU[1], D_all * bC[2] + (1 - D_all) * bU[2]) / kap
  inn <- sample(rc, BURN + TT, replace = TRUE) * sigma
  if (hetero) inn[-(1:BURN)] <- inn[-(1:BURN)] * hsc
  x <- mu + c(rep(0, BURN), b * e0) + inn
  as.numeric(stats::filter(x, c(f1, f2), method = "recursive"))[-(1:BURN)]
}
ybar_of <- function(g) sapply(pos, function(t) sum((5:1) * g[t:(t + 4)]) / 5)

fit <- function(y, X) {
  B <- solve(crossprod(X)); b <- B %*% crossprod(X, y); u <- as.numeric(y - X %*% b)
  h <- rowSums((X %*% B) * X)
  se <- function(uu, W) sqrt(diag(B %*% t(X * uu) %*% W %*% (X * uu) %*% B))
  list(b = as.numeric(b), nw = se(u, Wnw), nwhc3 = se(u / (1 - h), Wnw), dof = nrow(X) - ncol(X))
}
verdict <- function(bc, sc, bu, dof) {
  p <- pt(bc / sc, dof)
  padj <- p.adjust(p, "holm")
  sapply(1:2, function(i) {
    if (padj[i] < 0.05) 1L
    else if (pt(bc[i] / sc[i], dof, lower.tail = FALSE) < 0.05) 2L
    else if (bc[i] - qt(0.95, dof) * sc[i] > -OMEGA_MIN * abs(bu[i])) 3L
    else 4L
  })
}

# error de diseño (σ = 0, NW irrelevante: solo β̂)
gd <- sim_g(c(bref, bref), c(bref, bref), sigma = 0)
fd <- fit(ybar_of(gd), X_of(gd))
cat("error de diseño m=1 (C+,U+,C-,U-):", sprintf("%.6f", fd$b[3:6] - bref), "\n")
# comprobación determinista de los estimadores (y sin ruido): ee y s1_lin, para comparar con el script Python
fl <- fit(ybar_of(gd), cbind(1, eps, X_of(gd)[, 7:16]))
cat("determinista: ee NW5", sprintf("%.9f", fd$nw[3:6]), "| ee NW5-HC3", sprintf("%.9f", fd$nwhc3[3:6]),
    "| s1_lin b, ee", sprintf("%.9f", c(fl$b[2], fl$nwhc3[2])), "\n")

run <- function(m, c = 1, reps = REPS, hetero = FALSE) {
  bC <- rep(c * m * bref, 2); bU <- rep(c * bref, 2)
  truth <- c(bC[1], bU[1], bC[2], bU[2])
  cov <- list(NW5 = 0, `NW5-HC3` = 0)
  ver <- list(NW5 = matrix(0, 2, 4), `NW5-HC3` = matrix(0, 2, 4))
  lin <- 0; joint <- c(0, 0)
  for (r in seq_len(reps)) {
    g <- sim_g(bC, bU, hetero = hetero); y <- ybar_of(g); X <- X_of(g)
    f <- fit(y, X); tc <- qt(0.975, f$dof)
    for (k in names(cov)) {
      se <- if (k == "NW5") f$nw else f$nwhc3
      cov[[k]] <- cov[[k]] + (abs(f$b[3:6] - truth) <= tc * se[3:6])
      v <- verdict(f$b[c(3, 5)], se[c(3, 5)], f$b[c(4, 6)], f$dof)
      ver[[k]][1, v[1]] <- ver[[k]][1, v[1]] + 1; ver[[k]][2, v[2]] <- ver[[k]][2, v[2]] + 1
      if (k == "NW5-HC3") vh <- v
    }
    XL <- cbind(1, eps, X[, 7:16]); fl <- fit(y, XL)
    h0 <- pt(fl$b[2] / fl$nwhc3[2], fl$dof) < 0.05
    lin <- lin + h0; joint <- joint + (h0 & vh == 1L)
  }
  tag <- sprintf("m=%g c=%g hetero=%s", m, c, hetero)
  for (k in names(cov))
    cat(sprintf("[%s] %s: cobertura %s; subida %s; bajada %s\n", tag, k, paste(sprintf("%.3f", cov[[k]] / reps), collapse = " "),
                paste(sprintf("%.3f", ver[[k]][1, ] / reps), collapse = " "), paste(sprintf("%.3f", ver[[k]][2, ] / reps), collapse = " ")))
  cat(sprintf("[%s] P(H0 confirma)=%.3f; P(H0 y confirma H1+, H1-)= %.3f %.3f\n", tag, lin / reps, joint[1] / reps, joint[2] / reps))
}

cat("(veredictos: confirma, refuta_a, refuta_b, no_concluyente; cobertura: C+, U+, C-, U-)\n")
run(1)
if (ONLY_M1) quit(save = "no")
run(0)
run(1, c = 40, reps = REPS %/% 2)
run(1, hetero = TRUE)
