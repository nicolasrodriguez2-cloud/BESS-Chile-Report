# Pipeline semanal BESS Chile — diseño

Fecha: 2026-11-27 · Estado: **aprobado por Nicolás con dos ajustes**: (1) las primeras corridas semanales son en modo "solo avisar" (ver 5.11) y (2) el primer paso del plan es probar la descarga de PDFs desde GitHub Actions (ver 5.1). Nada de esto está construido todavía.

## 1. Intención

Hoy un agente (Claude) lee cada mes 4 reportes en PDF, interpreta un CLAUDE.md de ~220 líneas, edita `Información_reportes_Mensuales.xlsx` y abre un PR que Nicolás debe fusionar. Funciona, pero:

- Cuesta mucho para lo que es: una corrida real gastó ~85 créditos de Firecrawl más una sesión larga, y casi todo el trabajo es mecánico (copiar 6 números de una tabla).
- Las fuentes publican en fechas muy distintas (Generadoras se atrasa ~5 semanas, Coordinador publica a fin de mes, Min. Energía a mitad de mes), así que una corrida mensual siempre deja huecos.
- El PR es una revisión que Nicolás ya no quiere: solo él usa el Excel, y toma "la última versión de GitHub" para su PPT.

**Qué se quiere:** que el Excel se mantenga solo, al menor costo posible, y que nadie intervenga salvo que algo falle. El PPT "BYD Chile Market Report" **sigue manual**.

## 2. Alcance

**Dentro:** las 4 fuentes que quedan (ACERA, Generadoras, Coordinador, Min. Energía), la hoja BESS (filas 2-15), la hoja Energy Matrix, la tabla unificada ACERA, validaciones, publicación y alertas.

**Fuera (no-objetivos):**
- Energía Abierta y el gráfico "Evolución capacidad BESS" (se omiten por decisión de Nicolás).
- Automatizar el PPT, estimar market share, agregar fuentes nuevas, cualquier interfaz.
- Evadir bloqueos de cualquier fuente (proxy, user-agent falso, navegador sigiloso). Se mantiene la política actual.

**Anti-objetivos (fracaso aunque "funcione"):**
- Publicar un número equivocado sin que nadie se entere.
- Sobrescribir en silencio un dato que ya estaba en el Excel.
- Usar un modelo para lo que un script resuelve igual.
- Perder los gráficos nativos del Excel (chart2).

## 3. Restricciones

- El Excel es un `.xlsx` con gráfico nativo (`chart2`, el pie de Energy Matrix). Guardarlo con `openpyxl` borra los gráficos: la escritura debe hacerse a nivel XML del archivo (ya probado en esta sesión) y dejar byte a byte idénticas las partes que no cambian.
- Min. Energía bloquea todo acceso automático (WAF, 403 en todo el dominio). Sus PDFs los sube Nicolás a `MIN ENERGIA/`. Se leen de la carpeta, nunca del sitio.
- Datos que solo existen como imagen: en Min. Energía, la lámina de la página 6 ("Sistemas de Almacenamiento en ejecución") trae "declarado en construcción" y el total como etiquetas de imagen.
- Los PDFs de ACERA salen de `cdn.acera.cl` (sin robots.txt propio; se lee el de `www.acera.cl`, ya configurado como `robots_url`).
- Los hechos de cada fuente (período real, desfases, anomalías) están en `CLAUDE.md` actual y son punto de partida de las reglas del código.

## 4. Enfoques considerados

| | Qué es | Contra |
|---|---|---|
| **A. Seguir con el agente mensual** | Lo de hoy, con CLAUDE.md más corto | Sigue caro, deja huecos, requiere PR |
| **B. Script + pruebas, agente solo para excepciones** | Python determinista corre solo; un modelo lee únicamente la lámina de Min. Energía; un agente interviene solo si hay que reparar un extractor | Hay que construir y mantener código y pruebas |
| **C. Todo con un modelo vía API** | Un script que manda cada PDF a un modelo | Sigue pagando por tarea mecánica y es menos verificable |

**Elegido por Nicolás: B** (con corrida semanal, commit directo condicionado a validaciones, alerta solo ante fallos).

## 5. Diseño

### 5.1 Qué corre y dónde (mi decisión)
Un paquete Python (`pipeline/`) invocado por un cron **semanal** de GitHub Actions. El script es el mismo si más adelante se prefiere correrlo desde otra parte. **Primer paso del plan (confirmado por Nicolás): probar que desde un runner de GitHub Actions se pueden bajar los PDFs de las 3 fuentes abiertas, antes de construir nada más.** Si alguna fuente bloquea esas IPs, no se evade: se corre desde otro lugar (por ejemplo una Routine de Claude Code con el mismo script) o esa fuente pasa a manual.

### 5.2 Extractor por fuente
Un módulo por fuente, anclado en **textos del documento** (títulos de tabla, rótulos), nunca en número de página ni en el nombre del archivo.

| Fuente | De dónde salen los datos | Celdas que alimenta |
|---|---|---|
| ACERA | Tabla 6 "Capacidad instalada de Almacenamiento…", fila BESS (MW – MWh, tres estados). Período: título de la tabla ("Octubre-26") | E, J, P, T, AA, AE |
| Generadoras | Tabla de configuraciones (suma de filas = total) y texto "x MW (y MWh)". Período: carátula | C, I, M, S, Y, AD |
| Min. Energía | Párrafo de resumen (operativos, pruebas, construcción) y tablas de sistemas; "declarado en construcción" y total de la lámina (imagen). Período: "al {día} de {mes} de {año}" | D, N, Z (Z = construcción + declarado) |
| Coordinador | Tabla 1.1 de capacidad por tecnología y Fig. 2 de centrales en pruebas (suma de las barras "+BESS"). Período: "al cierre de {mes}" | Energy Matrix (columna nueva), O |

Reglas que se heredan: el **período real** sale del contenido; Coordinador y E. Abierta traen datos del mes anterior; si el sitio tiene varias versiones (`-v2`) vale la más nueva.

### 5.3 Lámina de Min. Energía (única lectura que hace Claude; cambio pedido por Nicolás)
No se usa la API de Anthropic: la lectura la hace **Claude en una sesión de Claude Code**. El script (GitHub Actions) detecta el PDF nuevo en `MIN ENERGIA/`, saca del texto todo lo que se puede (columnas D y N), renderiza la página de la lámina a imagen y deja la tarea anotada como pendiente (`estado/pendientes.json`). Una tarea programada de Claude Code corre cada semana y termina enseguida si no hay pendientes (mi decisión; la alternativa es que Nicolás pida "lee la lámina" a mano después de subir el PDF). Claude lee de la imagen **solo dos números**: "declarado en construcción" y el total del semicírculo, y los deja en `estado/`. Se valida contra el texto del mismo informe: operativos + pruebas + construcción (del párrafo) + declarado debe sumar el total (tolerancia ±2 MW por redondeo). Si no cuadra o la imagen no se lee clara, no se carga: `Z` queda vacío, el pendiente sigue abierto y se alerta. Mientras el pendiente está abierto, solo `Z` espera: `D` y `N` se publican normal. El costo corre por el uso de Claude de Nicolás, no por facturación de API. Si el "declarado" es idéntico al del mes anterior, se carga pero se marca "posible dato desactualizado".

### 5.4 Corrida semanal que solo actualiza lo que cambió
Un manifiesto (`estado/manifiesto.json`) guarda, por fuente y período: URL, sha256 y los valores extraídos. Cada semana el script:
1. Detecta reportes nuevos (patrón de URL de ACERA, listados de Generadoras y Coordinador, carpeta `MIN ENERGIA/` para los PDFs que sube Nicolás). No se vuelve a consultar el sitio de Min. Energía (siempre 403).
2. Para cada reporte con hash nuevo: extrae, valida y escribe solo las celdas de su fuente y mes.
3. **Nunca sobrescribe una celda que ya tiene dato.** Si un reporte nuevo cambia un valor ya cargado (por ejemplo una versión `-v2`), no lo toca y alerta.
4. También completa huecos de meses anteriores cuando el PDF existe y el extractor pasa sus pruebas.

### 5.5 Validaciones (puerta para publicar)
Por cada fuente, independientemente (una fuente que falla no frena a las demás):
- El período leído coincide con el esperado.
- Filas suman el total (Generadoras); categorías suman el total dentro de 0,2 % (Coordinador; entre 0,2 % y 1 % se publica y se anota como "anomalía"; más de 1 % se bloquea).
- MWh/MW entre 2 y 8 horas.
- Variación contra el mes anterior dentro de un rango razonable (a definir con el histórico); fuera de rango → no se publica esa celda.
- Excel resultante: se reabre, se recalcula con LibreOffice sobre una copia y los valores guardados coinciden; `chart2` y las demás partes sin cambios quedan idénticas byte a byte.

### 5.6 Publicación y alertas
- Si todo pasa, **commit directo a `main`** con el Excel y el manifiesto. Sin PR. El Excel queda siempre en la misma ruta del repo.
- **Alerta solo ante fallos** (mi decisión): el script abre (o actualiza) un Issue de GitHub con la lista de fuentes que fallaron y por qué. GitHub avisa por correo. Cuando una corrida posterior sí pasa, el Issue se cierra solo. Una semana sin reportes nuevos o sin fallos no genera ningún mensaje.

### 5.7 Pruebas con el histórico
Las pruebas ejecutan cada extractor sobre los PDFs que ya están en el repo y comparan con el Excel. Cobertura actual disponible: ACERA ene–oct (marzo, septiembre y octubre se bajaron en esta sesión y están sin commit), Generadoras ene–may y septiembre, Coordinador feb–sep, Min. Energía ene–oct. Meses sin PDF quedan fuera de las pruebas. Donde la prueba y el Excel discrepan, el caso se lista para que Nicolás decida cuál manda (el Excel tiene valores históricos calculados a mano, por ejemplo la columna O del Coordinador).

### 5.8 Mantenimiento
`CLAUDE.md` se reduce a unas 30 líneas: política de acceso (no evadir bloqueos), cómo está organizado el pipeline y qué hacer cuando un extractor falla. Cuando un formato cambie, un agente repara el extractor y las pruebas guían el arreglo.

### 5.9 Limpieza única del Excel y del repo
**Se hace al final del proyecto, en un commit aparte, y antes se crea el tag `pre-limpieza`** (así se puede volver atrás). Con E. Abierta fuera: quitar `chart1`, las filas 17-57 y las columnas H y X de la hoja BESS; eliminar la carpeta `E ABIERTA/` (~64 MB) y `historial/` (git ya guarda las versiones). Los PDFs que **ya están** en el repo (ACERA, Generadoras, Coordinador, Min. Energía) se quedan: son el material de las pruebas del 5.7. Hacia adelante, de ACERA, Generadoras y Coordinador **no se guardan PDFs nuevos** (se guarda URL y hash en el manifiesto); de Min. Energía sí, porque no se pueden volver a bajar solos. La hoja "Market Share Estimate" no se borra (contiene Main Future Projects).

**Verificación previa obligatoria (pedida por Nicolás):** antes de borrar, comprobar que `chart1` y las columnas H y X no alimentan el PPT. El `.pptx` está fuera del repo, así que hace falta una copia: la sube Nicolás, o se busca en su Drive con el conector si está ahí. Se leen los gráficos y vínculos del PPT y se listan las hojas y rangos de este Excel que referencian. El `.pptx` no se modifica. Si algo del PPT depende de lo que se iba a borrar, se detiene la limpieza y se pregunta.

### 5.10 Main Future Projects (mi decisión)
La primera versión **no modifica** esa lista. El script escribe los candidatos a alta o baja (proyectos ≥ ~1.000 MWh que aparecen o pasan a operación en las tablas de Min. Energía) en `estado/candidatos_proyectos.md`, sin alerta. La lista se actualiza cuando Nicolás lo pida.

### 5.11 Modo "solo avisar" al inicio (ajuste de Nicolás)
Las primeras 3 o 4 corridas semanales hacen todo el trabajo (detectar, extraer, validar, armar el Excel nuevo) pero **no hacen commit**. Una variable del repo (`PUBLICAR`) controla el modo; Nicolás la cambia a `true` cuando decide activar el commit directo.
- En este modo la corrida **informa cada semana, incluso si todo salió bien** (mi decisión): un resumen con las celdas que habría escrito, sus valores anteriores y las validaciones, más el Excel propuesto como archivo adjunto de la corrida para abrirlo y compararlo. Al activar el commit directo, las alertas vuelven a ser solo ante fallos.
- Criterio sugerido para activarlo (mi decisión): 3 o 4 corridas sin falsos errores y con al menos 2 reportes nuevos procesados y revisados por Nicolás. Como las fuentes publican una vez al mes, si en esas semanas casi no hay reportes nuevos, el modo se extiende; las pruebas con el histórico (5.7) cubren mientras tanto.

## 6. Decisiones de Nicolás (respondidas el 2026-11-27)

1. **Sin API de Anthropic (cambio del 2026-11-27, reemplaza su respuesta anterior):** la lectura de la lámina de Min. Energía la hace Claude en una sesión de Claude Code (ver 5.3). No hace falta clave ni límite de gasto.
2. **Limpieza del 5.9: sí, pero al final,** en un commit aparte y con el tag `pre-limpieza`. Antes de borrar se verifica que `chart1` y las columnas H y X no alimenten el PPT.
3. **Punto de partida del Excel:** se sube a `main` antes del plan, junto con los 5 PDFs de respaldo y este diseño, mostrándole antes el diff del Excel.

## 7. Qué queda para quien construya
Estructura de carpetas y librerías, rangos de variación (a partir del histórico), día y hora del cron, formato exacto del manifiesto, y la prueba de viabilidad desde GitHub Actions descrita en 5.1.
