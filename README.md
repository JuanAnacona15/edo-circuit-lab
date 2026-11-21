# ⚡ EDO Circuit Lab

**Laboratorio interactivo de ecuaciones diferenciales aplicadas a circuitos RC y RL.**

Aplicación educativa en Python que integra **electrónica**, **matemáticas** y
**computación**: modela los circuitos RC y RL, deduce y resuelve sus ecuaciones
diferenciales, aplica el método de ecuaciones exactas (con factores
integrantes), analiza datos experimentales por regresión lineal y valida los
resultados con SymPy y SciPy.

---

## ¿Qué es y para qué sirve?

El proyecto de aula pide demostrar, sobre dos circuitos eléctricos de primer
orden, todo el ciclo de las ecuaciones diferenciales ordinarias:

1. **Deducir** la EDO a partir de las leyes de Kirchhoff.
2. **Verificar** si la ecuación es exacta.
3. **Calcular** el factor integrante que la vuelve exacta.
4. **Resolver** el problema de valor inicial (analíticamente).
5. **Comprobar** la solución con Python (SymPy y SciPy).
6. **Interpretar** las gráficas, el campo de direcciones y el efecto de los
   parámetros.

El programa no es una simple calculadora: **muestra el procedimiento paso a
paso** y explica el significado físico de cada resultado.

| Circuito | Rol en el proyecto | EDO | Solución |
|----------|--------------------|-----|----------|
| **RC** (descarga) | *Problema real* (datos medidos) | $\dfrac{dV}{dt}=-\dfrac{V}{\tau}$ | $V(t)=V_0 e^{-t/\tau}$ |
| **RL** | *Ejercicio complementario* (R=4 Ω, L=2 H, E₀=12 V) | $L\dfrac{di}{dt}+Ri=E_0$ | $i(t)=3(1-e^{-2t})$ |

---

## Funcionalidades (módulos)

| Módulo | Qué hace |
|--------|----------|
| 🏠 **Inicio** | Presentación y navegación |
| 🔋 **Simulador RC** | Carga/descarga del capacitor, τ directa o R·C, gráfica interactiva, marcas 1τ/3τ/5τ |
| 🧲 **Simulador RL** | Corriente en la bobina, botón "cargar ejercicio del proyecto", explicación de R y L |
| 🧮 **Ecuaciones exactas** | Criterio ∂M/∂y = ∂N/∂x, factor integrante μ(x) o μ(y), función potencial, solución implícita/explícita/PVI, **paso a paso** |
| 📊 **Datos experimentales** | Carga los 50 datos o importa CSV, regresión de ln(V) vs t, estima V₀, τ y R², tabla y gráficas |
| ⚖️ **Comparación y validación** | Solución simbólica (SymPy) vs numérica (SciPy/RK45), error absoluto y relativo, verificación de la EDO y la condición inicial |
| 🧭 **Campo de direcciones** | Campo de pendientes + variación de condiciones iniciales y parámetros |
| 📄 **Informes** | Exporta CSV y genera informe en Markdown (PDF opcional) |

---

## La matemática, en resumen

### Circuito RC (descarga)

Ley de tensiones de Kirchhoff: $V_R + V_C = 0$, con $V_R=Ri$ e $i=-C\frac{dV}{dt}$:

$$RC\frac{dV}{dt}+V=0 \;\Rightarrow\; \frac{dV}{dt}=-\frac{V}{\tau},\qquad \tau=RC$$

Separando variables e integrando con $V(0)=V_0$:

$$V(t)=V_0\,e^{-t/\tau}$$

A $t=\tau$ queda el 36,8 % del voltaje; a $5\tau$ el 0,7 % (≈99,3 % descargado).
Matemáticamente nunca llega a 0: $\lim_{t\to\infty}V(t)=0$.

### Circuito RL

$$L\frac{di}{dt}+Ri=E_0 \;\Rightarrow\; i(t)=\frac{E_0}{R}+\left(i_0-\frac{E_0}{R}\right)e^{-(R/L)t},\qquad \tau=\frac{L}{R},\quad I_\infty=\frac{E_0}{R}$$

### Ecuaciones exactas y factor integrante

Para $M(x,y)\,dx+N(x,y)\,dy=0$, la condición de exactitud es
$\frac{\partial M}{\partial y}=\frac{\partial N}{\partial x}$. Si no se cumple:

- Si $\frac{M_y-N_x}{N}$ depende solo de $x$ → $\mu(x)=\exp\!\int\!\frac{M_y-N_x}{N}\,dx$
- Si $\frac{N_x-M_y}{M}$ depende solo de $y$ → $\mu(y)=\exp\!\int\!\frac{N_x-M_y}{M}\,dy$

Luego se construye el potencial $F=\int\tilde M\,dx+g(y)$ y la solución es $F(x,y)=C$.

- **RC:** $(V/\tau)\,dt+1\,dV=0$ → no exacta → $\mu(t)=e^{t/\tau}$.
- **RL:** $(Ri-E_0)\,dt+L\,di=0$ → no exacta → $\mu(t)=e^{(R/L)t}$.

### Regresión de los datos experimentales

Tomando logaritmos, el modelo exponencial se linealiza:

$$\ln V=\ln V_0-\frac{1}{\tau}\,t \;\Rightarrow\; y=b+m\,t$$

Ajustando por mínimos cuadrados se obtienen $V_0=e^b$ y $\tau=-1/m$, y se calcula
$R^2$ para medir la bondad del ajuste. Con el dataset del proyecto se recuperan
$\tau\approx 0{,}4896$ s y $R^2\approx 0{,}9991$.

> Cada módulo de `core/` documenta la deducción completa de estas ecuaciones
> en su docstring, con comentarios línea a línea.

---

## Instalación y puesta en marcha

Requisitos: **Python 3.10+** (probado con 3.11) y `pip`.

```bash
# 1. Clonar el repositorio
git clone https://github.com/JuanAnacona15/edo-circuit-lab.git
cd edo-circuit-lab

# 2. (Recomendado) crear un entorno virtual
python3 -m venv .venv
source .venv/bin/activate          # en Windows: .venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar la aplicación
streamlit run app.py
```

Streamlit abrirá el navegador en `http://localhost:8501`. La app funciona
**sin conexión** una vez instaladas las dependencias.

### Ejecutar las pruebas

```bash
python tests/test_core.py
```

### Regenerar el dataset (opcional)

```bash
python scripts/generate_volts.py
```

---

## Stack tecnológico

| Tecnología | Uso |
|------------|-----|
| [Python](https://www.python.org) | Lenguaje principal |
| [Streamlit](https://streamlit.io) | Interfaz web interactiva |
| [SymPy](https://www.sympy.org) | Álgebra simbólica (derivadas, integrales, `dsolve`) |
| [SciPy](https://scipy.org) | `solve_ivp` con método RK45 |
| [NumPy](https://numpy.org) | Cálculo vectorial |
| [Pandas](https://pandas.pydata.org) | Manejo de datos experimentales |
| [Matplotlib](https://matplotlib.org) | Figuras científicas (campo de direcciones) |
| [Plotly](https://plotly.com) | Gráficas interactivas |
| (opcional) ReportLab | Exportación a PDF |

---

## Estructura del proyecto

```
edo_circuit_lab/
├── app.py                  # punto de entrada (navegación)
├── requirements.txt
├── README.md
├── .streamlit/config.toml  # tema visual
├── pages/                  # interfaz (Streamlit)
│   ├── inicio.py
│   ├── circuito_rc.py
│   ├── circuito_rl.py
│   ├── ecuaciones_exactas.py
│   ├── datos_experimentales.py
│   ├── comparacion.py
│   ├── campo_direcciones.py
│   └── informes.py
├── core/                   # lógica matemática (sin UI)
│   ├── rc_model.py
│   ├── rl_model.py
│   ├── exact_equations.py
│   ├── symbolic_solver.py
│   ├── numerical_solver.py
│   ├── regression.py
│   └── validation.py
├── utils/                  # visualización, formato y exportación
│   ├── plotting.py
│   ├── formatting.py
│   └── export.py
├── data/
│   ├── Volts.csv           # 50 mediciones (reconstruidas)
│   └── sample_data.csv     # ejemplo sin ruido para probar importación
├── scripts/generate_volts.py
└── tests/test_core.py      # pruebas de aceptación
```

La separación por capas (presentación / aplicación / lógica / datos) permite
probar y corregir cada módulo por separado.

---

## Nota sobre los datos experimentales

El documento del proyecto da los parámetros de referencia ($V_0\approx 9{,}2128$ V,
$\tau\approx 0{,}4896$ s, $R^2\approx 0{,}9991$) pero **no incluye las 50
mediciones completas**. El archivo `data/Volts.csv` es una **reconstrucción
sintética** coherente con esos valores (generada con `scripts/generate_volts.py`,
semilla fija, ruido gaussiano ≈1,75 %), de modo que la regresión reproduce los
resultados del documento. Para usar datos reales, impórtalos desde la sección
"Datos experimentales" (CSV con columnas `Time` y `Voltage`).

---

## Criterios de aceptación verificados

| Prueba | Resultado esperado |
|--------|--------------------|
| Cargar el conjunto Volts | 50 mediciones |
| Ejecutar regresión | τ ≈ 0,4896 s |
| Calcular R² | ≈ 0,9991 |
| Cargar el circuito RL | R=4, L=2, E₀=12 |
| Corriente estacionaria RL | 3 A |
| Constante de tiempo RL | 0,5 s |
| Resolver RL con SymPy | $3(1-e^{-2t})$ |
| Verificar ecuación original | No exacta |
| Aplicar factor integrante | Ecuación exacta |
| Comparar métodos | Diferencia numérica pequeña |

Todas se ejecutan automáticamente con `python tests/test_core.py`.

---

## Licencia

Proyecto académico (Proyecto de Aula EDO – Grupo 3). Uso libre con fines
educativos.
