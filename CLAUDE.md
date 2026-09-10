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
/GENERADORAS/	Generadoras.cl — Boletines Mensuales	⚠️ Pendiente de confirmar	Hasta confirmar si el acceso automatizado es viable (ver sección abajo), la Routine trata esta carpeta igual que Coordinador/Ministerio: lee de acá, no intenta bajar sola. Si se confirma que se puede automatizar, pasa al mismo patrón que ACERA/E. Abierta.
Por qué Coordinador y Ministerio de Energía quedan en manual

Coordinador: su robots.txt declara explícitamente User-agent: ClaudeBot → Disallow: / — decisión declarada del sitio dirigida específicamente al crawler de Anthropic, no un bloqueo técnico incidental. No se evade de ninguna forma — ni cambiando identidad/user-agent, ni pidiendo un asset estático puntual en vez de navegar el sitio, aunque esa ruta responda 200 técnicamente. El robots.txt sigue diciendo "no" a nivel de dominio completo, y esa directiva se respeta.

Ministerio de Energía: WAF (Radware) devuelve 403 en todo el dominio energia.gob.cl — panel, PDFs sueltos, y probablemente su propio robots.txt. A diferencia de Coordinador, acá no hay una declaración tipo robots.txt de por medio — es un bloqueo técnico indiscriminado. El resultado práctico es el mismo (fuente no accesible), por un motivo distinto.

Si en algún momento se consigue una vía de acceso autorizada de cualquiera de las dos instituciones (API key vigente, whitelist de IP, convenio de datos, etc.), se actualiza esta sección y esa fuente pasa al patrón de ACERA/E. Abierta.

Pendiente — Generadoras.cl

Un PDF suelto de generadoras.cl/wp-content/uploads/... respondió 200 en una prueba anterior — el bloqueo tipo captcha (Sucuri) visto antes puede no aplicar a esa ruta. Falta confirmar si la página de listado (generadoras.cl/category/boletines-mensuales/) carga sin challenge; si sí, el acceso automatizado es viable (mismo patrón que ACERA) y esta fuente sale de la tabla de "manual". Si también bloquea, se confirma como manual definitivo.

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

Market Share Estimate (a definir dónde vive exactamente)

Investigación abierta (no limitada a las 5 fuentes de arriba) para estimar participación de mercado BESS por proveedor. No hay fuente oficial — es una estimación. Reglas:

Documentar metodología en cada corrida: qué proyectos se usaron, qué fabricante se les atribuyó y con qué fuente, qué quedó sin confirmar.
Un proyecto sin fabricante identificable con confianza razonable se excluye del cálculo, no se le asigna uno a ojo.
Nunca presentar el resultado con más precisión de la que la metodología sostiene.
Incluye altas/bajas de la lista de "Main future projects" (≥ ~1000 MWh): alta cuando se identifica un proyecto nuevo, baja cuando entra en operación. La Routine puede agregar/quitar filas acá sin señalizar para revisión previa (no es una decisión estructural), pero siempre queda en el changelog.
Qué NO hace esta Routine
No toca ningún archivo .pptx — vive fuera de este repo.
No inventa el período de un dato cuando el reporte fuente no lo deja claro — lo señaliza.
No rellena con estimación propia una celda vacía porque una fuente no publicó a tiempo — la deja vacía y lo nota en el changelog.
No intenta descargar por su cuenta los PDFs de /COORDINADOR/ ni /MIN ENERGIA/ (ni de /GENERADORAS/ mientras esté pendiente de confirmar) — solo los lee si ya están subidos.
No evade bloqueos declarados (robots.txt) ni técnicos (WAF/captcha) de ninguna fuente, bajo ninguna forma.
No mergea su propio PR. No renombra, reordena ni elimina carpetas ni hojas sin señalizarlo — incluidos los archivos sin extensión de origen desconocido en cada carpeta de fuente.
Changelog de cada corrida (formato, va en la descripción del PR)
## Corrida AAAA-MM

### Hoja BESS — filas 2-15
- [bloque]: [mes] → [valor(es) nuevos], fuente [X]
- Huecos rellenados retroactivamente: [mes/fuente/bloque, si aplica]
- Huecos que quedan pendientes: [fuente que no había publicado al momento
  de la corrida]

### Fuentes automatizadas (ACERA, E. Abierta [, Generadoras si se confirma])
- PDF fetcheado y archivado en /[CARPETA]/[nombre]: período verificado
  [mes/año]

### Fuentes manuales procesadas esta corrida (Coordinador / Min. Energía [/ Generadoras si sigue manual])
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

### Market Share Estimate
- Metodología de esta corrida: [proyectos usados, fuentes, supuestos]
- Altas/bajas en Future Projects: [...]

### Períodos verificados manualmente (reportes con desfase mes X vs X-1)
[cualquier caso donde el nombre del reporte no coincidía con el período
real de los datos]

### Fuentes sin publicación / sin acceso a la fecha de esta corrida
[cuáles de las 5 no tenían informe disponible, o siguen bloqueadas]
