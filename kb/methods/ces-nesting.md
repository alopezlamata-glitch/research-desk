# Convertir un debate de forma funcional en un test sobre un parámetro (anidamiento CES)

**Problema típico:** "¿los canales se suman o se multiplican?" se resuelve comparando
especificaciones ad hoc (AIC/BIC entre modelos distintos). Eso es débil y es fácil hacer
"forking paths".

**Receta:** agrega los canales $s_j \in (0,1]$ con un CES generalizado

$$ T(s) = A\Big[\sum_j w_j s_j^{\rho}\Big]^{\nu/\rho}, \qquad w_j>0,\ \sum_j w_j = 1 $$

- $\rho = 1$: aditivo (los canales son sustitutos perfectos).
- $\rho \to 0$: Cobb-Douglas $A\prod_j s_j^{\nu w_j}$ (multiplicativo; con $\nu w_j=1$ es el producto puro).
- $\rho \to -\infty$: Leontief $A\min_j s_j^{\nu}$ (cuello de botella puro: solo importa el canal peor).

Con eso, "¿hay cuello de botella?" pasa a ser una hipótesis sobre $\rho$ (p. ej., $H_0:\rho=1$
frente a $\rho<1$), con un intervalo de confianza en lugar de una comparación entre modelos.
La elasticidad de sustitución entre canales es $1/(1-\rho)$.

**Trampas:**
- $\rho$ está mal identificado si los canales apenas se mueven por separado: necesitas episodios
  en los que un canal esté mal y los otros bien. Comprueba la identificación con Monte Carlo.
- El límite $\rho\to 0$ es numéricamente inestable: implementa la rama Cobb-Douglas explícitamente
  cuando $|\rho|<10^{-6}$.
- Las cross-partials de $T$ son positivas para todo $\rho<1$, así que su signo no distingue
  "multiplicativo" de "otras complementariedades". Lo que hay que testear es el valor de $\rho$.

Origen: p01 (transmission bottlenecks), 2026-11.
