# Explicación del código — Proyecto Numérico

App de Streamlit (`streamlit run main.py`) con los métodos numéricos de cuatro
unidades: raíces de ecuaciones, sistemas lineales, integración numérica y
ecuaciones diferenciales.

## 1. Arquitectura

```
main.py            -> arranca la app y decide qué pantalla mostrar
algoritmos/        -> lógica pura (cálculo), sin Streamlit
interfaces/        -> pantallas: piden datos, llaman a algoritmos/ y muestran resultados
```

La separación es estricta: los archivos de `algoritmos/` no importan nada de
Streamlit y se pueden usar o probar solos. Cada método tiene dos archivos:

- `algoritmos/<unidad>/<metodo>.py` con una función `resolver_<metodo>(...)`
  que **devuelve un diccionario** con los resultados (raíz, tabla, error, etc.)
  y **lanza `ValueError`** con un mensaje en español si los datos no son válidos.
- `interfaces/<unidad>/pantalla_<metodo>.py` con una función `mostrar()`.

### Flujo de una ejecución

1. `main.py` llama a `mostrar_barra_lateral()` (`interfaces/barra_lateral.py`),
   que dibuja dos `selectbox`: unidad y método (sacados del diccionario `UNIDADES`).
2. Con `(unidad, metodo)` busca en el diccionario `PANTALLAS` la función
   `mostrar` correspondiente y la ejecuta.
3. La pantalla pide los datos. Si no se presiona el botón, termina (`return`).
4. Al presionarlo llama a `resolver_...` dentro de un `try`; si hay
   `ValueError` lo muestra con `st.error` y termina.
5. Si todo sale bien, muestra métricas, fórmula en LaTeX, gráfica y tabla.

Para agregar un método: crear los dos archivos, añadir el nombre en `UNIDADES`
(`barra_lateral.py`) y la entrada en `PANTALLAS` (`main.py`).

## 2. Interpretación de funciones — `algoritmos/funciones.py`

Todo método recibe la función como **texto** (por ejemplo `x^3 - x - 2`).
Este módulo la convierte en algo evaluable usando **sympy** en lugar de `eval`,
así no se puede ejecutar código arbitrario.

- `_normalizar(texto)`: reemplaza símbolos del teclado por su equivalente
  (`π → pi`, `√ → sqrt`, `× → *`, `÷ → /`, `− → -`, `² → ^2`, `³ → ^3`).
- `_parsear(limpio, nombres, texto)`: llama a `sympy.parse_expr` con las
  transformaciones `convert_xor` (`^` es potencia) e
  `implicit_multiplication_application` (`2x`, `3sin(x)`, `(x+1)(x-1)`).
  El diccionario `NOMBRES` añade alias: `ln`, `log10`, `sen`, `raiz`, `abs`, `e`, `pi`.
  Cualquier error de parseo se convierte en `ValueError`.
- `interpretar(texto, con_y=False)`: valida que no esté vacío, que solo dependa
  de `x` (o de `x` e `y` para EDOs) y que no tenga números imaginarios.
- `interpretar_numero(texto)`: para las celdas de las matrices. Acepta `1/3`,
  `√2`, `2π`, `2,5` (coma decimal) y devuelve `(valor_float, expresion)`.
  Rechaza variables y complejos.
- `crear_funcion(texto)`: devuelve `(f, expresion)` donde `f = lambdify(x, ...)`,
  una función de Python que acepta números o arrays de NumPy.
- `crear_funcion_xy(texto)`: igual pero `f(x, y)`, para `y' = f(x, y)`.
- `derivar(expresion)`: derivada simbólica exacta con `sp.diff`; devuelve
  `(f', expresion_derivada)`. La usan Newton y punto fijo, así el usuario solo
  escribe `f(x)`.

## 3. Unidad 1 — Raíces de ecuaciones (`algoritmos/raices/`)

Todos devuelven al menos `raiz`, `convergio`, `expresion` y `f` (para graficar).

### Bisección — `biseccion.py`
- Requiere `a < b` y que `f(a)` y `f(b)` tengan signos opuestos
  (teorema de Bolzano); si no, `ValueError`.
- Usa `scipy.optimize.bisect(f, a, b, xtol=tol, maxiter=max_iter, full_output=True)`:
  parte el intervalo a la mitad y se queda con la mitad donde hay cambio de signo.
- Devuelve raíz, `f(raíz)`, iteraciones y si convergió (de `info`).

### Posición falsa (regla falsa) — `posicion_falsa.py`
Programado a mano porque SciPy no lo trae.
- Mismas validaciones que bisección.
- En cada iteración calcula el corte con el eje x de la recta que une
  `(a, f(a))` y `(b, f(b))`:
  `c = b − f(b)·(b − a) / (f(b) − f(a))`.
- Guarda una fila `{iteración, a, b, c, f(c)}` en `tabla`.
- Para si `f(c) = 0` o si `|c − c_anterior| < tol`.
- Si `f(a)·f(c) < 0` la raíz está en `[a, c]` (se mueve `b`), si no en `[c, b]` (se mueve `a`).

### Punto fijo — `punto_fijo.py`
- El usuario escribe `g(x)` (el despeje `x = g(x)`), no `f(x)`.
- Usa `scipy.optimize.fixed_point(..., method="iteration")`: la iteración
  clásica `xₙ₊₁ = g(xₙ)` (sin `method="iteration"` SciPy usaría aceleración de Steffensen).
- Si no converge (o se desborda) lanza `ValueError` sugiriendo otro despeje,
  recordando la condición `|g'(x)| < 1`.
- Devuelve también `g'(raíz)` para justificar la convergencia.

### Newton-Raphson — `newton.py`
- Calcula `f'` simbólicamente con `derivar`.
- Si `f'(x0) = 0` la tangente es horizontal → `ValueError`.
- Usa `scipy.optimize.newton(f, x0, fprime=df, ...)`, que itera
  `xₙ₊₁ = xₙ − f(xₙ)/f'(xₙ)`.
- Devuelve también la expresión de la derivada.

### Secante — `secante.py`
- Requiere `x0 ≠ x1`.
- Usa `scipy.optimize.newton(f, x0, x1=x1, ...)` **sin** `fprime`: en ese caso
  SciPy aplica la secante, que aproxima la derivada con los dos últimos puntos:
  `xₙ₊₁ = xₙ − f(xₙ)·(xₙ − xₙ₋₁)/(f(xₙ) − f(xₙ₋₁))`.

## 4. Unidad 2 — Sistemas lineales (`algoritmos/sistemas_lineales/`)

### Validación común — `validacion.py`
`validar_sistema(A, b)` convierte a arrays de NumPy y verifica: `A` cuadrada,
`b` del mismo tamaño, sin celdas vacías/no numéricas, y `rank(A) = n`
(si no, `A` es singular y no hay solución única). Todos los métodos la llaman primero.

Todos devuelven el **residuo** `‖Ax − b‖∞`, que mide qué tan bien cumple `x` el sistema.

### Eliminación de Gauss — `gauss.py`
- Arma la matriz aumentada `[A | b]` y la convierte a sympy con números
  **racionales exactos** (`sp.Rational(str(valor))`) para evitar errores de redondeo.
- `LUdecomposition()` de esa matriz da como `U` exactamente la matriz escalonada
  que resulta de la eliminación hacia adelante. Si hubo pivote cero, sympy
  intercambia filas y devuelve la lista de `intercambios` (se muestran como `F1 ↔ F2`).
- La solución `x` se calcula con `numpy.linalg.solve`.

### Factorización LU (Doolittle, sin pivoteo) — `lu.py`
- `A` en racionales exactos → `L, U, intercambios = A.LUdecomposition()`.
- Si hubo intercambios, la LU sin pivoteo no existe → `ValueError` sugiriendo LUP.
- Resuelve en dos pasos con las funciones de `sustitucion.py`:
  `Ly = b` (hacia adelante) y luego `Ux = y` (hacia atrás).
- Devuelve `L`, `U`, `y`, `x`.

### Factorización LUP (pivoteo parcial) — `lup.py`
- `scipy.linalg.lu(A)` devuelve `P, L, U` con `A = P·L·U`. En clase se usa
  `PA = LU`, así que se transpone: `P = P_scipy.T`.
- La solución se obtiene con `lu_solve(lu_factor(A), b)`.
- Devuelve `P`, `L`, `U`, `Pb` y `x`.

### Sustitución hacia adelante / atrás — `sustitucion.py`
Programadas a mano porque son los pasos internos de LU/LUP.
- `_validar_triangular`: matriz cuadrada, tamaños coherentes, valores finitos y
  diagonal sin ceros (si no, no se puede despejar).
- `sustitucion_hacia_adelante(L, b)`: para `i = 0 … n−1`,
  `yᵢ = (bᵢ − Σ_{j<i} Lᵢⱼ·yⱼ) / Lᵢᵢ`.
- `sustitucion_hacia_atras(U, y)`: para `i = n−1 … 0`,
  `xᵢ = (yᵢ − Σ_{j>i} Uᵢⱼ·xⱼ) / Uᵢᵢ`.
- La suma se hace como producto punto de NumPy (`L[i, :i] @ y[:i]`).

### Jacobi — `jacobi.py` y Gauss-Seidel — `gauss_seidel.py`
Iterativos, programados a mano. Estructura idéntica:
- Rechazan ceros en la diagonal (habría que dividir entre `aᵢᵢ`).
- Parten de `x0` (o del vector cero) y guardan cada iteración en `tabla`
  (fila 0 = valor inicial).
- En cada iteración: `xᵢ = (bᵢ − Σ_{j≠i} aᵢⱼ·xⱼ) / aᵢᵢ`.
  - **Jacobi** usa solo los valores de la iteración anterior (`x_anterior`) para todos los `j`.
  - **Gauss-Seidel** usa los `xⱼ` **ya actualizados** en esta iteración para
    `j < i` y los anteriores para `j > i`; por eso suele converger más rápido.
- Error = `‖x⁽ᵏ⁾ − x⁽ᵏ⁻¹⁾‖∞`; para cuando `error < tol` (convergió) o si
  aparecen infinitos/NaN (divergió).
- `es_diagonal_dominante(A)`: `|aᵢᵢ| > Σ_{j≠i} |aᵢⱼ|` en todas las filas.
  Es condición suficiente de convergencia y se informa en la pantalla.

## 5. Unidad 3 — Integración numérica (`algoritmos/integracion/`)

### Elementos comunes — `elementos.py`
- `preparar(texto, a, b, n)`: valida `a < b` y `n ≥ 1`, calcula
  `h = (b − a)/n`, los nodos `xᵢ = a + i·h` (`np.linspace`) y `f(xᵢ)`.
  Si `f` no es finita en algún nodo lanza `ValueError` indicando dónde.
  (El `np.broadcast_to` cubre funciones constantes, que devuelven un escalar.)
- `valor_referencia(f, a, b)`: integral "real" con `scipy.integrate.quad`
  (adaptativo) para calcular el error real; `None` si no converge.
- `maximo_derivada(expresion, orden, a, b)`: deriva simbólicamente `orden`
  veces y aproxima `max |f⁽ᵏ⁾|` evaluando en 1001 puntos. Se usa en las cotas.

### Trapecio compuesto — `trapecio.py`
- `∫ₐᵇ f ≈ h/2 · [f(x₀) + 2f(x₁) + … + 2f(xₙ₋₁) + f(xₙ)]`.
- La suma la hace `scipy.integrate.trapezoid(ys, xs)`.
- Construye los coeficientes `1, 2, …, 2, 1` solo para mostrarlos en la tabla.
- Cota del error: `|E| ≤ (b − a)·h²/12 · max|f''|`.

### Simpson 1/3 compuesto — `simpson.py`
- Exige `n` par (`n ≥ 2`).
- `∫ₐᵇ f ≈ h/3 · [f(x₀) + 4f(x₁) + 2f(x₂) + … + 4f(xₙ₋₁) + f(xₙ)]`.
- La suma la hace `scipy.integrate.simpson(ys, x=xs)`, que con `n` par
  (número impar de nodos) es exactamente esta fórmula.
- Coeficientes `1, 4, 2, 4, …, 2, 4, 1` para la tabla.
- Cota del error: `|E| ≤ (b − a)·h⁴/180 · max|f⁽⁴⁾|`.

Ambos devuelven `aproximacion`, `h`, `referencia`, `error` real, `cota`,
la derivada usada en la cota y la `tabla` de nodos.

### Sumas superiores e inferiores (Darboux) — `riemann.py`
- En cada subintervalo `[xᵢ, xᵢ₊₁]` muestrea `f` en 101 puntos para
  aproximar el mínimo `mᵢ` y el máximo `Mᵢ`.
- Suma inferior `Σ mᵢ·h` y superior `Σ Mᵢ·h`; la integral queda acotada:
  `I_inf ≤ ∫f ≤ I_sup`.
- Estimación = promedio de ambas; `acotamiento = superior − inferior`
  (se reduce al aumentar `n`).
- Ignora puntos no finitos dentro del subintervalo; si todos lo son, `ValueError`.

## 6. Unidad 4 — Ecuaciones diferenciales (`algoritmos/ecuaciones_diferenciales/`)

Problema de valor inicial: `y' = f(x, y)`, `y(x₀) = y₀`, en `[x₀, x_final]` con `n` pasos.

### Elementos comunes — `valor_inicial.py`
- `preparar(...)`: valida `x_final > x₀` y `n ≥ 1`, crea `f(x, y)`,
  `h = (x_final − x₀)/n` y la malla `xᵢ = x₀ + i·h`.
- `evaluar(f, xi, yi)`: evalúa `f` y lanza `ValueError` si el resultado no es
  finito (la solución "explotó"), sugiriendo un `h` menor.
- `derivada_parcial_y(expresion)`: `∂f/∂y`. Si `f` y `∂f/∂y` son continuas
  cerca de `(x₀, y₀)`, el PVI tiene solución única (teorema de existencia y
  unicidad); la pantalla lo muestra.
- `solucion_referencia(...)`: para medir el error. Si el usuario escribió la
  solución exacta `y(x)`, la evalúa en la malla; si no, usa
  `scipy.integrate.solve_ivp` (método `DOP853`, tolerancias `1e-11/1e-12`).
  Devuelve `(valores, origen)` o `(None, motivo)`.

### Euler — `euler.py`
Programado a mano (SciPy no trae Euler de paso fijo).
- `yᵢ₊₁ = yᵢ + h·f(xᵢ, yᵢ)`: avanza por la recta tangente.
- Tabla con `i, xᵢ, f(xᵢ, yᵢ), yᵢ` y, si hay referencia, `y(xᵢ)` y `|error|`.
- Error global `O(h)`.

### Runge-Kutta 4 (clásico) — `runge_kutta.py`
Programado a mano (`solve_ivp` con RK45 es adaptativo, no el RK4 de paso fijo de clase).
```
k₁ = f(xᵢ, yᵢ)
k₂ = f(xᵢ + h/2, yᵢ + h·k₁/2)
k₃ = f(xᵢ + h/2, yᵢ + h·k₂/2)
k₄ = f(xᵢ + h,   yᵢ + h·k₃)
yᵢ₊₁ = yᵢ + h/6 · (k₁ + 2k₂ + 2k₃ + k₄)
```
- Tabla con `k₁ … k₄` en cada paso, más referencia y error si existen.
- Error global `O(h⁴)`.

Ambos devuelven `xs`, `ys`, `h`, `y_final`, `referencia`, `error_final`, `df_dy` y `tabla`.

## 7. Interfaces (`interfaces/`)

### Compartidas
- `barra_lateral.py`: diccionario `UNIDADES` y `mostrar_barra_lateral()`.
- `teclado.py`: teclado matemático tipo GeoGebra. Guarda el texto en
  `st.session_state[clave]` y la posición del cursor en
  `st.session_state[clave_cursor(clave)]`. Las teclas que terminan en `(`
  (`sin(`, `sqrt(`, `^(`) se cierran solas y dejan el cursor adentro;
  `⌫` borra una función completa si corresponde; `←`/`→` mueven el cursor.
  Pestañas "123" y "f(x)"; con `con_y=True` añade la tecla `y` (EDOs).
  `al_escribir_a_mano` sincroniza cuando el usuario escribe directamente en el `text_input`.
- `notacion.py`: `texto_a_latex(texto, cursor=None, decimal_coma=False)`
  convierte el texto a LaTeX **tal cual se escribió** (sympy lo
  simplificaría/reordenaría). Tiene su propio tokenizador y parser con la
  misma precedencia que `funciones.py` (`+ −` < `× ÷` e implícita < `−` unario < `^`).
  Lo que falta en una función a medio escribir se muestra como `□` y devuelve
  `incompleta=True`; también dibuja el cursor en color.

### Por unidad
- `raices/entrada_funcion.py` — `pedir_funcion(...)`: vista previa en LaTeX +
  teclado + campo de texto. Cada `pantalla_<metodo>.py` pide los parámetros
  (`a`, `b` o `x0`, `x1`, tolerancia, máx. iteraciones), muestra la raíz,
  iteraciones, `f(raíz)` y la gráfica de `f` junto a `y = 0`.
  Posición falsa muestra además la tabla de iteraciones.
- `sistemas_lineales/componentes.py` — `entrada_sistema(prefijo)`: elige `n`,
  muestra el sistema como ecuaciones alineadas en LaTeX y las celdas de
  `A | b` editables con el teclado o a mano (cada celda se interpreta con
  `interpretar_numero`). `mostrar_matriz`, `mostrar_vector` y
  `mostrar_solucion` dibujan los resultados en LaTeX.
- `integracion/componentes.py` — `entrada_integral` (f, a, b, n),
  `mostrar_resultado` (aproximación, referencia, error real, cota y la
  derivada usada), `graficar` (f junto a la curva que la regla integra:
  segmentos para el trapecio, parábolas para Simpson) y `mostrar_tabla`.
- `ecuaciones_diferenciales/componentes.py` — `entrada_pvi` (f(x, y), x₀, y₀,
  x final, n, solución exacta opcional) y `mostrar_resultado` (y(x final),
  error, `∂f/∂y`, gráfica aproximación vs. referencia y tabla de pasos).

## 8. Dependencias (`requirements.txt`)

| Librería  | Uso |
|-----------|-----|
| streamlit | interfaz web |
| sympy     | interpretar texto, derivadas simbólicas, LU exacta |
| scipy     | bisect, newton, fixed_point, lu, trapezoid, simpson, quad, solve_ivp |
| numpy     | arrays, normas, `linalg.solve` |
| pandas    | tablas y gráficas (`st.dataframe`, `st.line_chart`) |
