CLAUDE.md — BESS-Chile-Report

Repo fuente de verdad para el agente "Capacidad BESS Chile". Corre como Claude Code Routine mensual. Este documento es lo que la Routine lee al empezar cada corrida — no asumas contexto fuera de este archivo y de los datos ya presentes en el repo.

Rol de la Routine

Una vez al mes, actualizás Información_reportes_Mensuales.xlsx (datos + los 2 gráficos nativos ya existentes en el archivo) a partir de 5 fuentes públicas sobre BESS y matriz eléctrica en Chile, directo en tu rama, y abrís un Pull Request con el archivo editado + changelog + copia fechada en /historial/. Nunca mergeás tu propio PR.

Este archivo es el mismo Excel al que apunta (por link externo roto, ya no relevante) el gráfico del PPT "BYD Chile Market Report" — es la fuente real, no una copia. La Routine solo toca este repo; el PPT se actualiza aparte, manualmente, en una sesión de Chat distinta.

Estructura del repo (real, no inferida)
/ACERA/            ← PDFs de ACERA, un archivo por mes
/COORDINADOR/      ← PDFs del Coordinador, un archivo por mes
/E ABIERTA/        ← PDFs de Energía Abierta, un archivo por mes
/GENERADORAS/      ← PDFs de Generadoras.cl, un archivo por mes
/MIN ENERGIA/      ← PDFs de Ministerio de Energía, un archivo por mes
/Información_reportes_Mensuales.xlsx   ← archivo oficial, un solo activo
/historial/AAAAMMDD_Información_reportes_Mensuales.xlsx
/CLAUDE.md
/README.md

⚠️ Dos de estos cinco nombres de carpeta tienen espacio (E ABIERTA, MIN ENERGIA). Al construir paths en scripts, siempre con comillas o escapado — un path sin comillas se rompe silenciosamente ahí.

⚠️ Cada carpeta tiene además un archivo sin extensión con un nombre corto (Acera, Coord, Gen, Min, E ABIERTA) que no corresponde al patrón de los reportes reales. No se sabe qué son — la Routine los ignora al procesar (no son PDFs, no tienen fecha reconocible) y no los borra ni los toca; si conviene limpiarlos, es una decisión de Nicolás, no de la Routine.

Cómo se relaciona cada carpeta con el método de acceso de su fuente
Carpeta	Fuente	Acceso	Qué hace la Routine con la carpeta
/ACERA/	ACERA — Boletín Estadísticas	✅ Automatizado (URL predecible)	La Routine fetchea la URL del mes, y además guarda una copia del PDF acá como respaldo/auditoría de qué documento sustenta cada cifra cargada. Nunca lee de acá para obtener el dato — siempre fetch en vivo; la copia es solo registro.
/E ABIERTA/	Energía Abierta — Reporte mensual del sector energético	✅ Automatizado	Mismo patrón que ACERA: fetch en vivo + copia de respaldo en la carpeta.
/COORDINADOR/	Coordinador Eléctrico Nacional — Informe Mensual	❌ Manual (robots.txt: Disallow / para ClaudeBot — ver más abajo)	La Routine lee de acá, nunca intenta bajar el PDF sola. Nicolás sube el PDF del mes navegando el sitio como cualquier persona.
/MIN ENERGIA/	Ministerio de Energía — Reporte de Proyectos	❌ Manual (WAF/403 en todo el dominio)	Igual que Coordinador: la Routine solo lee de acá.
/GENERADORAS/	Generadoras.cl — Boletines Mensuales	✅ Automatizado (confirmado en la corrida 2026-10)	Mismo patrón que ACERA/E. Abierta: fetch en vivo del boletín del mes + copia de respaldo en la carpeta. Ver nota de acceso más abajo (el slug del post no siempre coincide con el mes del título).
Por qué Coordinador y Ministerio de Energía quedan en manual

Coordinador: su robots.txt declara explícitamente User-agent: ClaudeBot → Disallow: / — decisión declarada del sitio dirigida específicamente al crawler de Anthropic, no un bloqueo técnico incidental. No se evade de ninguna forma — ni cambiando identidad/user-agent, ni pidiendo un asset estático puntual en vez de navegar el sitio, aunque esa ruta responda 200 técnicamente. El robots.txt sigue diciendo "no" a nivel de dominio completo, y esa directiva se respeta.

Ministerio de Energía: WAF (Radware) devuelve 403 en todo el dominio energia.gob.cl — panel, PDFs sueltos, y probablemente su propio robots.txt. A diferencia de Coordinador, acá no hay una declaración tipo robots.txt de por medio — es un bloqueo técnico indiscriminado. El resultado práctico es el mismo (fuente no accesible), por un motivo distinto.

Si en algún momento se consigue una vía de acceso autorizada de cualquiera de las dos instituciones (API key vigente, whitelist de IP, convenio de datos, etc.), se actualiza esta sección y esa fuente pasa al patrón de ACERA/E. Abierta.

Generadoras.cl — resuelto (corrida 2026-10)

Confirmado: generadoras.cl/robots.txt sólo prohíbe /wp-admin/, y la página de listado generadoras.cl/category/boletines-mensuales/ responde 200 sin challenge (el bloqueo tipo Sucuri visto antes ya no aplica). La fuente queda automatizada.

Cómo se navega:

1. Listado: https://generadoras.cl/category/boletines-mensuales/ (www. redirige 301 al dominio sin www; seguir el redirect).
2. En el listado, ubicar la entrada por el **título** ("Boletín Generadoras de Chile – MES AAAA"), no por el slug del link. ⚠️ El slug no siempre coincide: el boletín de **Junio 2026** vive en `/boletin-generadoras-de-chile-mayo-2026-2/`. Construir la URL adivinando el mes devuelve una página 200 que no es el boletín buscado.
3. Dentro del post, el PDF está en un `href` a `generadoras.cl/wp-content/uploads/AAAA/MM/...pdf`. En algunos posts el link se arma por JS; si no aparece un `href` .pdf, buscar la cadena `.pdf` en el HTML.

⚠️ Período dentro del boletín: el dato de almacenamiento que usa este repo está en la **página 6** y corresponde al mes del título del boletín. Dos advertencias:
- Los boletines hasta mayo-2026 imprimían "información de asociados a MES de 2026" en la página 6; desde junio-2026 el layout nuevo ya no imprime esa línea. En su lugar, verificar contra la página 4 (DESTACADOS), cuyos peaks están fechados dentro del mes del título.
- La página 4 de los boletines viejos repetía la cifra de almacenamiento del mes **anterior** (en el boletín de mayo-26 decía 13.174 MWh, que es el valor de abril). **La página 6 manda siempre.**
- Otras secciones del mismo boletín sí van desfasadas (la página 5, capacidad de generación, viene "a junio de 2026" en el boletín de agosto-2026). No mezclar.

URLs de las otras dos fuentes automatizadas (verificadas en la corrida 2026-10)

ACERA: la página de estadísticas (acera.cl/estadisticas-del-sector-de-generacion-de-energia-electrica-renovable/) arma los links por JS, así que no sirve raspar su HTML. La vía estable es la API REST de WordPress:

`https://www.acera.cl/wp-json/wp/v2/media?search=Boletin-Estadisticas&per_page=20&orderby=date&order=desc&_fields=date,source_url`

Devuelve los PDFs servidos desde `cdn.acera.cl/wp-content/uploads/AAAA/MM/AAAA-MM-Boletin-Estadisticas-ACERA.pdf`. ⚠️ El mes del nombre del archivo es el mes **del dato**; la carpeta `/AAAA/MM/` de la URL es el mes de **publicación** (el boletín de agosto-26 está bajo `/2026/09/`). Se publica alrededor de la mitad del mes siguiente, así que una corrida a mitad de mes puede encontrar que el boletín del mes anterior todavía no salió. El dato que usa este repo está en la Tabla 6 ("Capacidad instalada de Almacenamiento según avance de los proyectos"), última página del boletín.

Energía Abierta / CNE: el listado es energiaabierta.cl/reportes/ y los PDFs están alojados en cne.cl: `https://www.cne.cl/wp-content/uploads/AAAA/MM/RMensual_vAAAAMM.pdf` (no confundir con `RMensual_ERNC_v...`, que es otro reporte). El capítulo 2 (BESS) está en la página 5 y declara explícitamente el período: "conforme a la Resolución Exenta N.° XXX, con fecha 31 de MES de AAAA" — ese es el período real del dato, un mes antes del nombre del archivo.

⚠️ La serie de las filas 17-57 sale del gráfico "Evolución capacidad de almacenamiento BESS – Según fecha estimada de interconexión" de esa misma página. Es un gráfico de eje **categórico**: sólo aparecen los meses con valor distinto de cero, y las etiquetas del eje salen una categoría por medio. Para leerlo hay que extraer las etiquetas de datos con sus coordenadas X (pdfplumber `chars`) y alinearlas contra las etiquetas de mes del eje; contar barras a ojo da el mes equivocado. Si aparece una categoría nueva sin etiqueta de eje que la ancle, su mes no es determinable desde el gráfico: se señaliza en el changelog, no se adivina.

Regla crítica de todas las fuentes

Algunos reportes se publican bajo el nombre del mes "X" pero contienen datos correspondientes al mes "X-1" (confirmado para Coordinador y Energía Abierta; ACERA no tiene este desfase). Antes de cargar cualquier cifra — venga de fetch automático o de un PDF ya en el repo — verificar dentro del documento mismo a qué período corresponde el dato. Nunca asumir el período por el nombre del archivo, la carpeta, ni el mes de publicación. Si el período real no queda claro en el documento, señalizarlo en el changelog en vez de adivinar.

Estructura exacta del archivo Información_reportes_Mensuales.xlsx
Hoja "BESS"

Filas 2-15 — seis tablas mes a mes (2026), cada una con columnas fijas por fuente (no todas las fuentes alimentan todas las tablas):

Bloque (fila 2)	Rango cols	Fuentes que reportan esta métrica (fila 3)
BESS in operation MW	C:E	Generadoras, Min. Energía, ACERA
BESS in operation MWh	H:J	E. Abierta, Generadoras, ACERA
BESS in test MW	M:P	Generadoras, Min. Energía, Coordinador, ACERA
BESS in test MWh	S:T	Generadoras, ACERA
BESS in construction MW	X:AA	E. Abierta, Generadoras, Min. Energía, ACERA
BESS in construction MWh	AD:AE	Generadoras, ACERA

Coordinador solo alimenta "BESS in test MW" — su informe mensual no reporta capacidad en operación ni en construcción, solo lo que está en etapa de pruebas en el SEN. No forzar un dato de Coordinador en las otras cinco tablas.

Es normal y esperado que queden celdas vacías en un mes si esa fuente específica todavía no publicó su informe para ese mes al momento de la corrida — la Routine no rellena con estimaciones propias. Si en una corrida posterior una fuente publica retroactivamente el dato de un mes anterior que había quedado vacío, sí se completa ese hueco histórico (no solo se avanza con el mes en curso).

Filas 17-57 — "Evolución capacidad BESS operativo" (mismos datos que Energía Abierta llama "según fecha estimada de interconexión" — es la misma serie, dos nombres distintos para lo mismo):

Columnas: Month (fecha), Year, Acumulado [MWh], Mensual [MWh]
Fuente única: Energía Abierta.
Alimenta chart1 del archivo (nativo, ya existe — no recrear, solo actualizar los valores cacheados o agregar filas si corresponde).
Extiende hacia 2027-2029 con proyectos ya conocidos — al agregar el mes en curso, no se tocan las proyecciones futuras salvo que la fuente las actualice explícitamente.
Hoja "Energy Matrix"

Filas 3-13 — tabla mensual con las categorías tal como las reporta el Coordinador (10 categorías: Reservoir Hydraulics, Run of the River Hydraulics, Natural Gas, Coal, Diesel, Other thermal, Eolic, Solar Thermal, Solar PV, Geothermal + Total). Se agrega una columna nueva cada mes con el dato del informe del Coordinador. Fuente única: Coordinador (vía /COORDINADOR/, carga manual).

Filas 16-25 — tabla resumen del mes más reciente, con categorías combinadas (Hydric = Reservoir + Run of the River; Solar = Solar PV + Solar Thermal; el resto igual) + columna de %. Alimenta chart2 (el pie de capacidad instalada, el mismo que usa el PPT). Se recalcula cada mes tomando la última columna de la tabla de arriba y combinando categorías — no es un dato aparte, es una transformación de la tabla de arriba.

⚠️ Energy Matrix!C25 es un valor escrito a mano (no fórmula), y es el multiplicador de toda la columna B de la tabla resumen. Al agregar una columna nueva, actualizarlo junto con las referencias de C17:C24, o se descuadra en silencio la tabla que alimenta chart2.

Main Future Projects (≥ ~1000 MWh)

Investigación abierta (no limitada a las 5 fuentes de arriba) para identificar proyectos BESS relevantes en Chile por tamaño:

Alta: proyecto nuevo identificado con capacidad ≥ ~1000 MWh.
Baja: proyecto que pasó de "futuro/en desarrollo" a "en operación" — se saca de esta lista (el dato pasa a vivir en las tablas de operación correspondientes).
La Routine puede agregar/quitar filas acá sin señalizar para revisión previa (no es una decisión estructural), pero siempre queda en el changelog.
Tabla unificada ACERA — "BESS Situation in Chile"

Nueva tabla (hoja ACERA Summary, o al final de la hoja BESS — a elección de la Routine, dejarlo señalado en el changelog la primera vez que se cree) que consolida solo las columnas de fuente ACERA de las seis tablas de arriba, en el mismo formato que ACERA usa en su propio reporte: una fila por mes, tres bloques (Operation, Test, Construction), cada uno con sub-columnas MW y MWh.

Mapeo exacto (referencias a la hoja BESS, nunca valores hardcodeados — son fórmulas que apuntan a las celdas ya cargadas):

Columna de la tabla nueva	Referencia
Operation MW	=BESS!E{fila}
Operation MWh	=BESS!J{fila}
Test MW	=BESS!P{fila}
Test MWh	=BESS!T{fila}
Construction MW	=BESS!AA{fila}
Construction MWh	=BESS!AE{fila}

Formato visual de referencia: encabezado combinado "BESS Situation in Chile (ACERA, {año})", filas Enero-Diciembre, celda vacía si el dato ACERA de ese mes todavía no está cargado (no se estima, mismo criterio que el resto del archivo). Se actualiza sola cada corrida porque son fórmulas — la Routine no tiene que "llenarla" aparte, solo asegurarse de que las 6 columnas de origen (E, J, P, T, AA, AE) estén al día.

Qué NO hace esta Routine
No investiga ni estima participación de mercado por fabricante (market share) — se sacó del alcance porque la búsqueda abierta no encontraba información confiable y consumía tiempo/tokens sin resultado. Si en el futuro aparece una fuente concreta y verificable para esto, se reincorpora explícitamente al CLAUDE.md, no antes.
No toca ningún archivo .pptx — vive fuera de este repo.
No inventa el período de un dato cuando el reporte fuente no lo deja claro — lo señaliza.
No rellena con estimación propia una celda vacía porque una fuente no publicó a tiempo — la deja vacía y lo nota en el changelog.
No intenta descargar por su cuenta los PDFs de /COORDINADOR/ ni /MIN ENERGIA/ — solo los lee si ya están subidos.
No evade bloqueos declarados (robots.txt) ni técnicos (WAF/captcha) de ninguna fuente, bajo ninguna forma.
No mergea su propio PR. No renombra, reordena ni elimina carpetas ni hojas sin señalizarlo — incluidos los archivos sin extensión de origen desconocido en cada carpeta de fuente.
Changelog de cada corrida (formato, va en la descripción del PR)
## Corrida AAAA-MM

### Hoja BESS — filas 2-15
- [bloque]: [mes] → [valor(es) nuevos], fuente [X]
- Huecos rellenados retroactivamente: [mes/fuente/bloque, si aplica]
- Huecos que quedan pendientes: [fuente que no había publicado al momento
  de la corrida]

### Fuentes automatizadas (ACERA, E. Abierta, Generadoras)
- PDF fetcheado y archivado en /[CARPETA]/[nombre]: período verificado
  [mes/año]

### Fuentes manuales procesadas esta corrida (Coordinador / Min. Energía)
- [institución]: `/[CARPETA]/[nombre exacto del PDF]` → período real
  verificado dentro del documento: [mes/año] → celdas actualizadas: [...]
- PDFs presentes en la carpeta que aún no se incorporaron (si los hay,
  con motivo: ya estaban cargados / período no aplica / no se pudo
  determinar el período)

### Hoja BESS — filas 17-57 (Energía Abierta)
- Fila agregada/actualizada: [mes, acumulado, mensual]

### Hoja Energy Matrix
- Columna [mes] agregada a tabla 3-13 (Coordinador)
- Tabla resumen 16-25 recalculada con categorías combinadas
- Recordar actualizar C25 y C17:C24 si corresponde

### Main Future Projects
- Altas/bajas: [...]

### Tabla unificada ACERA
- Sin acción manual esperada (son fórmulas) — solo confirmar que no
  quedó ninguna celda de origen (E/J/P/T/AA/AE) sin actualizar este mes

### Períodos verificados manualmente (reportes con desfase mes X vs X-1)
[cualquier caso donde el nombre del reporte no coincidía con el período
real de los datos]

### Fuentes sin publicación / sin acceso a la fecha de esta corrida
[cuáles de las 5 no tenían informe disponible, o siguen bloqueadas]
