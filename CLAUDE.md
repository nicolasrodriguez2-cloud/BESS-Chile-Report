CLAUDE.md — BESS-Chile-Report
Repo = fuente de verdad. Agente "Capacidad BESS Chile". Routine mensual.
Lee este archivo al empezar cada corrida. No asumas nada fuera de este archivo y de lo que hay en el repo.
Rol
Una vez al mes, actualiza `Información_reportes_Mensuales.xlsx` (datos + los 2 gráficos nativos que ya existen).
Usa solo datos publicados en los reportes de 5 fuentes públicas.
Trabaja en tu rama. Abre un Pull Request con: Excel editado + changelog + copia fechada en `/historial/`.
Nunca hagas merge de tu propio PR.
Este Excel es la fuente real del gráfico del PPT "BYD Chile Market Report". El link externo viejo está roto, no importa.
No toques ningún `.pptx`. El PPT se actualiza aparte, a mano.
Alcance
Solo datos de los reportes de las 5 fuentes.
NO busques competidores, clientes, ferias, regulación ni market share. Otras tareas lo hacen.
Si algo te pide salir de este alcance: no lo hagas. Anótalo en el PR.
Estructura del repo
```
/ACERA/          PDFs de ACERA, uno por mes
/COORDINADOR/    PDFs del Coordinador, uno por mes
/E ABIERTA/      PDFs de Energía Abierta, uno por mes
/GENERADORAS/    PDFs de Generadoras.cl, uno por mes
/MIN ENERGIA/    PDFs del Ministerio de Energía, uno por mes
/Información_reportes_Mensuales.xlsx   archivo oficial, solo uno activo
/historial/AAAAMMDD_Información_reportes_Mensuales.xlsx
/fuentes.yml     lista de fuentes y qué método permite cada una
/scripts/fetch_fallback.py   plan B de acceso (solo HTTP)
/datos_crudos/AAAAMM/        salida del script. No tocar a mano.
/CLAUDE.md
/README.md
```
⚠️ `E ABIERTA` y `MIN ENERGIA` tienen espacio. En scripts usa siempre comillas. Sin comillas se rompe en silencio.
⚠️ Cada carpeta de fuente tiene un archivo sin extensión y nombre corto (Acera, Coord, Gen, Min, E ABIERTA). No se sabe qué son. Ignóralos. No los borres ni los toques. Limpiarlos es decisión de Nicolás.
Cómo entrar a cada fuente
Orden fijo:
Lee el `robots.txt` del dominio de la fuente. Si hay Disallow para tu ruta: es bloqueo de política. Ve al paso 3.
`firecrawl_scrape`, siempre con `proxy: "basic"`. Siempre primero. En modo auto, Firecrawl puede subir a proxy sigiloso ante un 403. Eso es evadir. No lo permitas.
Si falla por causa técnica y `fuentes.yml` dice `fallback_scrapling: true`: usa Scrapling.
Herramienta MCP `make_request`, o
`python scripts/fetch_fallback.py <url> --fuente <nombre>`.
Si hay bloqueo de política: para. Marca "carga manual". Lee el archivo de la carpeta de la fuente.
Tipo	Ejemplos	Qué haces
Fallo técnico	timeout, error 5xx, página vacía	Scrapling (si la fuente lo permite)
Bloqueo de política	robots.txt con Disallow, 403 en todo el dominio, captcha o desafío anti-bot	Parar. Carga manual.
Antes de usar Scrapling: lee el `robots.txt` del dominio. Si dice Disallow: para.
Si Scrapling da 401, 403 o 429: es bloqueo. Para. No reintentes.
Prohibido, siempre:
Evadir bloqueos. Ni de robots.txt ni de WAF ni de captcha.
Proxy. `impersonate`. `StealthyFetcher`. `solve_cloudflare`.
Cualquier herramienta `browser_*` de Scrapling.
Cambiar user-agent. Buscar una ruta alterna al mismo archivo.
Si Firecrawl y Scrapling fallan por causa técnica en una fuente automatizada:
deja la celda vacía. No inventes. Anota "sin dato este mes: fallo técnico" en el changelog.
Cada carpeta y su fuente
Carpeta	Fuente	Acceso	Qué hace la Routine
`/ACERA/`	ACERA — Boletín Estadísticas	✅ Automatizado (URL predecible). Scrapling permitido.	Lee el PDF del mes en vivo. Guarda copia del PDF aquí como respaldo. Nunca saques el dato de la carpeta: siempre en vivo. La copia es solo registro.
`/E ABIERTA/`	Energía Abierta — Reporte mensual del sector energético	✅ Automatizado. Scrapling permitido.	Igual que ACERA.
`/COORDINADOR/`	Coordinador Eléctrico Nacional — Informe Mensual	✅ Automatizado (robots.txt ya no bloquea, probado 2026-11-27). Scrapling permitido.	Igual que ACERA. Si el robots.txt vuelve a bloquear: pasa a manual y lee solo de aquí.
`/MIN ENERGIA/`	Ministerio de Energía — Reporte de Proyectos	❌ Manual (WAF, 403)	Igual que Coordinador.
`/GENERADORAS/`	Generadoras.cl — Boletines Mensuales	✅ Automatizado (listado público sin captcha, probado 2026-11-27). Scrapling permitido.	Igual que ACERA. Si vuelve el captcha: manual.
Si no puedes guardar el PDF de respaldo: anota URL + fecha + hash en el changelog.
Historial de bloqueos (revisado 2026-11-27)
Coordinador: antes su `robots.txt` decía `User-agent: ClaudeBot` → `Disallow: /`. Hoy (`www.coordinador.cl/robots.txt`) solo bloquea `/wp-admin/`, `/wp-includes/` y `/wp-content/`, con `Allow` para `/wp-content/uploads/*`. Ya no hay regla contra ClaudeBot. Pasa a automatizado.
Si el Disallow vuelve: manual otra vez. No se evade de ninguna forma. Ni cambiando identidad. Ni pidiendo un archivo suelto aunque responda 200.
Ministerio de Energía: su WAF (Radware) da 403 en todo `energia.gob.cl`, incluso en `robots.txt`. Probado 2026-11-27: el 403 siguió aunque Firecrawl subió solo a proxy sigiloso. Es un bloqueo técnico general contra acceso automático.
Sigue manual. Aunque una persona lo abra en su navegador, no se usa un navegador para saltar el bloqueo.
Si Nicolás consigue acceso autorizado (API key, whitelist de IP, convenio de datos), se actualiza esta sección. Esa fuente pasa al patrón de ACERA.
Generadoras.cl — resuelto
Probado 2026-11-27: su `robots.txt` solo bloquea `/wp-admin/`. El listado `generadoras.cl/category/boletines-mensuales/` carga con Firecrawl (proxy basic), sin captcha. Pasa al patrón de ACERA.
Si el captcha vuelve a aparecer: manual otra vez. No se evade.
Regla crítica: período real
Algunos reportes salen con nombre del mes "X" pero traen datos del mes "X-1".
Confirmado en Coordinador y Energía Abierta. ACERA no tiene este desfase.
Antes de cargar cualquier cifra (fetch en vivo o PDF ya en el repo): mira dentro del documento a qué período corresponde.
Nunca uses el nombre del archivo, la carpeta o el mes de publicación.
Si el período no queda claro: no adivines. Señálalo en el changelog.
Estructura exacta del Excel `Información_reportes_Mensuales.xlsx`
Hoja "BESS"
Filas 2-15. Seis tablas, mes a mes (2026). Columnas fijas por fuente. No todas las fuentes alimentan todas las tablas.
Bloque (fila 2)	Columnas	Fuentes (fila 3)
BESS in operation MW	C:E	Generadoras, Min. Energía, ACERA
BESS in operation MWh	H:J	E. Abierta, Generadoras, ACERA
BESS in test MW	M:P	Generadoras, Min. Energía, Coordinador, ACERA
BESS in test MWh	S:T	Generadoras, ACERA
BESS in construction MW	X:AA	E. Abierta, Generadoras, Min. Energía, ACERA
BESS in construction MWh	AD:AE	Generadoras, ACERA
Coordinador solo alimenta "BESS in test MW". Su informe no trae operación ni construcción. No fuerces un dato de Coordinador en las otras cinco tablas.
Celdas vacías son normales si la fuente aún no publicó ese mes. No rellenes con estimación.
Si una fuente publica tarde el dato de un mes viejo que estaba vacío: completa ese hueco. No avances solo con el mes en curso.
Filas 17-57. "Evolución capacidad BESS operativo". Es la misma serie que Energía Abierta llama "según fecha estimada de interconexión". Dos nombres, misma cosa.
Columnas: Month (fecha), Year, Acumulado [MWh], Mensual [MWh].
Fuente única: Energía Abierta.
Alimenta `chart1` (nativo, ya existe). No lo recrees. Solo actualiza valores o agrega filas.
Llega hasta 2027-2029 con proyectos ya conocidos. Al agregar el mes en curso, no toques las proyecciones futuras salvo que la fuente las cambie de forma explícita.
Hoja "Energy Matrix"
Filas 3-13. Tabla mensual con las categorías como las reporta el Coordinador:
Reservoir Hydraulics, Run of the River Hydraulics, Natural Gas, Coal, Diesel, Other thermal, Eolic, Solar Thermal, Solar PV, Geothermal + Total.
Cada mes se agrega una columna nueva con el dato del informe del Coordinador.
Fuente única: Coordinador (automatizado; respaldo del PDF en `/COORDINADOR/`).
Filas 16-25. Tabla resumen del mes más reciente, con categorías combinadas:
Hydric = Reservoir + Run of the River. Solar = Solar PV + Solar Thermal. El resto igual. Más columna de %.
Alimenta `chart2` (el pie de capacidad instalada, el mismo del PPT).
No es un dato aparte. Es una transformación de la última columna de la tabla de arriba. Recalcúlala cada mes.
⚠️ `Energy Matrix!C25` es un valor escrito a mano (no fórmula). Es el multiplicador de toda la columna B de la tabla resumen.
Al agregar una columna nueva, actualiza C25 y las referencias de C17:C24. Si no, la tabla que alimenta `chart2` se descuadra en silencio.
Main Future Projects (≥ ~1000 MWh)
Ya no hay búsqueda abierta. Solo mira lo que dicen los reportes de las 5 fuentes.
Alta: un reporte muestra un proyecto nuevo con capacidad ≥ ~1000 MWh.
Baja: un reporte muestra que el proyecto pasó a operación. Sácalo de la lista. El dato pasa a las tablas de operación.
Puedes agregar y quitar filas aquí sin pedir revisión antes. No es cambio estructural. Siempre va en el changelog.
Tabla unificada ACERA — "BESS Situation in Chile"
Tabla nueva (hoja `ACERA Summary`, o al final de la hoja BESS; elige tú y anótalo en el changelog la primera vez).
Junta solo las columnas ACERA de las seis tablas de arriba. Mismo formato que el reporte de ACERA: una fila por mes, tres bloques (Operation, Test, Construction), cada uno con MW y MWh.
Son fórmulas que apuntan a la hoja BESS. Nunca valores a mano.
Columna nueva	Referencia
Operation MW	`=BESS!E{fila}`
Operation MWh	`=BESS!J{fila}`
Test MW	`=BESS!P{fila}`
Test MWh	`=BESS!T{fila}`
Construction MW	`=BESS!AA{fila}`
Construction MWh	`=BESS!AE{fila}`
Formato: encabezado combinado "BESS Situation in Chile (ACERA, {año})". Filas Enero-Diciembre. Celda vacía si ACERA aún no cargó ese mes. No se estima.
Se actualiza sola porque son fórmulas. Solo asegura que las 6 columnas de origen (E, J, P, T, AA, AE) estén al día.
Qué NO hace esta Routine
No busca competidores, clientes, ferias ni regulación.
No estima market share por fabricante. Se sacó: la búsqueda no hallaba datos confiables y gastaba tokens. Solo vuelve si aparece una fuente concreta y verificable, y se escribe aquí.
No toca ningún `.pptx`.
No inventa el período de un dato. Si no está claro, lo señala.
No rellena una celda vacía con estimación propia.
No baja por su cuenta los PDFs de `/MIN ENERGIA/`. Solo los lee si ya están subidos. En cualquier otra fuente, si reaparece un bloqueo de política, pasa a manual y lee solo de la carpeta.
No evade bloqueos. Ni declarados (robots.txt) ni técnicos (WAF, captcha). De ninguna fuente. De ninguna forma.
No hace merge de su PR.
No renombra, reordena ni elimina carpetas ni hojas sin señalarlo. Incluye los archivos sin extensión de origen desconocido.
Antes de abrir el PR
Corre `arithmetic-check` sobre las cifras nuevas (sumas, %, MW × horas ≈ MWh).
Verifica el período real de cada cifra.
Muestra el diff: celda, valor viejo, valor nuevo, fuente.
No digas "listo" sin evidencia de estos pasos.
Si ninguna fuente tiene reporte nuevo: no abras PR. Deja "sin novedades" en una nota breve.
Changelog de cada corrida (va en la descripción del PR)
```
## Corrida AAAA-MM

### Hoja BESS — filas 2-15
- [bloque]: [mes] → [valor(es) nuevos], fuente [X], método [firecrawl / scrapling / manual]
- Huecos rellenados atrás: [mes/fuente/bloque, si aplica]
- Huecos pendientes: [fuente que no había publicado al correr]

### Fuentes automatizadas (ACERA, E. Abierta, Generadoras, Coordinador)
- PDF leído y archivado en /[CARPETA]/[nombre]: período verificado [mes/año], método [...]
- Fuente con fallo técnico: [cuál, qué pasó, celda quedó vacía]

### Fuentes manuales procesadas (Min. Energía, o cualquier fuente que pasó a manual esta corrida)
- [institución]: `/[CARPETA]/[nombre exacto del PDF]` → período real dentro del documento: [mes/año] → celdas actualizadas: [...]
- PDFs en la carpeta que no se incorporaron (con motivo: ya cargado / período no aplica / período no claro)

### Hoja BESS — filas 17-57 (Energía Abierta)
- Fila agregada/actualizada: [mes, acumulado, mensual]

### Hoja Energy Matrix
- Columna [mes] agregada en tabla 3-13 (Coordinador)
- Tabla resumen 16-25 recalculada con categorías combinadas
- C25 y C17:C24 actualizados: [sí/no]

### Main Future Projects
- Altas/bajas: [...]

### Tabla unificada ACERA
- Sin acción manual (son fórmulas). Confirmar que ninguna celda de origen (E/J/P/T/AA/AE) quedó sin actualizar.

### Alcance
- Algo fuera de alcance que se pidió y no se hizo: [...]
```
