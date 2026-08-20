CLAUDE.md — Capacidad-BESS-Chile

Repo fuente de verdad para el agente "Capacidad BESS Chile". Corre como Claude Code Routine mensual. Este documento es lo que la Routine lee al empezar cada corrida — no asumas contexto fuera de este archivo y de los datos ya presentes en el repo.

Rol de la Routine

Una vez al mes, investigás 5 fuentes públicas sobre BESS y matriz eléctrica en Chile, actualizás Informacion_reportes_Mensuales.xlsx (datos + los 2 gráficos nativos ya existentes en el archivo) directo en tu rama, y abrís un Pull Request con el archivo editado + changelog + copia fechada en /historial/. Nunca mergeás tu propio PR.

Este archivo es el mismo Excel al que apunta (por link externo roto, ya no relevante) el gráfico del PPT "BYD Chile Market Report" — es la fuente real, no una copia. La Routine solo toca este repo; el PPT se actualiza aparte, manualmente, en una sesión de Chat distinta.

Fuentes (5) y qué le corresponde a cada una
ACERA — Boletín Estadísticas — https://www.acera.cl/centro-de-informacion/
Ministerio de Energía — Reporte de Proyectos — https://energia.gob.cl/panel/reporte-de-proyectos
Coordinador Eléctrico Nacional — Informe Mensual — https://www.coordinador.cl/reportes/documentos/informe-mensual-coordinador-electrico-nacional/
Generadoras.cl — Boletines Mensuales — https://generadoras.cl/category/boletines-mensuales/
Energía Abierta — Reporte mensual del sector energético — http://energiaabierta.cl/reportes/
Método de acceso — Coordinador Eléctrico Nacional (importante)

El sitio del Coordinador publica un robots.txt con User-agent: ClaudeBot → Disallow: / — es una restricción declarada explícitamente para el crawler de Anthropic, no un bloqueo genérico (WAF/captcha) como los de Ministerio de Energía o Generadoras.cl. No se debe intentar evadir esto cambiando de identidad/user-agent ni con ninguna otra técnica de evasión — si el sitio decide bloquear a ClaudeBot, esa decisión se respeta.

Lo que sí cambia es cómo se pide el documento: en vez de navegar/crawlear el sitio (/reportes/documentos/...), la Routine intenta una descarga directa y puntual del PDF del mes, por URL predecible:

https://www.coordinador.cl/wp-content/uploads/{AAAA}/{MM}/CEN_Informe_Mensual_SEN_{MesAbrev}{AA}.pdf

({MesAbrev} = Ene/Feb/Mar/Abr/May/Jun/Jul/Ago/Sep/Oct/Nov/Dic; {AA} = año a 2 dígitos. Ejemplo confirmado: CEN_Informe_Mensual_SEN_Feb26.pdf. Recordar el desfase de un mes: el informe de {MM} trae datos de {MM}-1, así que para obtener el dato de un mes X hay que pedir el PDF de X+1.)

Orden de intento, sin insistir más allá de esto:

Fetch directo a la URL predicha para el mes que se necesita.
Si da 404 (no robots.txt), es que el patrón de nombre cambió ese mes — usar una búsqueda web puntual (no crawl del sitio) para localizar el PDF exacto y reintentar el fetch directo a esa URL.
Si el fetch (directo o vía URL encontrada por búsqueda) sigue bloqueado por el propio sitio, se marca Coordinador como fuente no accesible esta corrida en el changelog — igual que Ministerio de Energía o Generadoras.cl cuando bloquean. No es un fallo a resolver con más intentos, es una fuente señalizada.

Regla crítica de todas las fuentes: algunos reportes se publican bajo el nombre del mes "X" pero contienen datos correspondientes al mes "X-1". Antes de cargar cualquier cifra, verificar dentro del documento mismo a qué período corresponde el dato — nunca asumir el período por el nombre del archivo o el mes de publicación. Si el período real no queda claro en el documento, señalizarlo en el changelog en vez de adivinar.

Estructura exacta del archivo
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
Fuente única: Energía Abierta, gráfico "Evolución capacidad BESS – Según fecha estimada de interconexión" en su reporte mensual.
Alimenta chart1 del archivo (nativo, ya existe — no recrear, solo actualizar los valores cacheados o agregar filas si corresponde).
Extiende hacia 2027-2029 con proyectos ya conocidos — al agregar el mes en curso, no se tocan las proyecciones futuras salvo que la fuente las actualice explícitamente.
Hoja "Energy Matrix"

Filas 3-13 — tabla mensual con las categorías tal como las reporta el Coordinador (10 categorías: Reservoir Hydraulics, Run of the River Hydraulics, Natural Gas, Coal, Diesel, Other thermal, Eolic, Solar Thermal, Solar PV, Geothermal + Total). Se agrega una columna nueva cada mes con el dato del informe del Coordinador Eléctrico Nacional. Fuente única: Coordinador.

Filas 16-25 — tabla resumen del mes más reciente, con categorías combinadas (Hydric = Reservoir + Run of the River; Solar = Solar PV + Solar Thermal; el resto igual) + columna de %. Esta tabla es la que alimenta chart2 (el pie de capacidad instalada, el mismo que usa el PPT). Se recalcula cada mes tomando la última columna de la tabla de arriba (filas 3-13) y combinando las categorías — no es un dato aparte que haya que buscar en otra fuente, es una transformación de la tabla de arriba.

Market Share Estimate (nueva hoja, o sección dentro de una existente — a definir en el piloto)

Antes vivía como tarea manual en el Chat del PPT. Se mueve acá porque requiere investigación más profunda de la que un solo mes de las 5 fuentes fijas puede dar — la Routine tiene que hacer una búsqueda amplia (no limitada a las 5 fuentes de arriba) para identificar, mes a mes, qué proveedor (CATL, Sungrow, Wärtsilä, Fluence, Tesla, Trina, Huawei, e-STORAGE, otros) está detrás de los proyectos BESS identificados en Chile, y construir una estimación de participación de mercado a partir de eso.

No hay fuente oficial de market share BESS en Chile — esto sigue siendo una estimación, no una cifra dura. Reglas:

Documentar la metodología en cada corrida: qué proyectos se usaron, qué fabricante se les atribuyó y con qué fuente, qué quedó sin confirmar.
Si un proyecto no tiene fabricante identificable con confianza razonable, no se le asigna uno "a ojo" — se excluye del cálculo y se nota como excluido.
Nunca presentar el resultado con más precisión de la que la metodología sostiene (evitar decimales falsos de precisión).
Esta sección sí puede requerir búsqueda web general (noticias, comunicados de prensa de los fabricantes, licitaciones adjudicadas), no solo las 5 fuentes fijas — a diferencia del resto de este documento, que se limita a esas 5.
Qué NO hace esta Routine
No toca ningún archivo .pptx — vive fuera de este repo.
No inventa el período de un dato cuando el reporte fuente no lo deja claro — lo señaliza.
No rellena con estimación propia una celda vacía porque una fuente no publicó a tiempo — la deja vacía y lo nota en el changelog.
No mezcla las categorías del Coordinador con las de otra fuente en la tabla de filas 3-13 — esa tabla es Coordinador puro.
No mergea su propio PR. No renombra, reordena ni elimina hojas sin señalizarlo.
Estructura del repo
/Informacion_reportes_Mensuales.xlsx     ← archivo oficial, un solo activo
/historial/AAAAMMDD_Informacion_reportes_Mensuales.xlsx
/README.md
/CLAUDE.md
Changelog de cada corrida (formato, va en la descripción del PR)
## Corrida AAAA-MM

### Hoja BESS — filas 2-15
- [bloque]: [mes] → [valor(es) nuevos], fuente [X]
- Huecos rellenados retroactivamente: [mes/fuente/bloque, si aplica]
- Huecos que quedan pendientes: [fuente que no había publicado al momento
  de la corrida]

### Hoja BESS — filas 17-57 (Energía Abierta)
- Fila agregada/actualizada: [mes, acumulado, mensual]

### Hoja Energy Matrix
- Columna [mes] agregada a tabla 3-13 (Coordinador)
- Tabla resumen 16-25 recalculada con categorías combinadas

### Períodos verificados manualmente (reportes con desfase mes X vs X-1)
[cualquier caso donde el nombre del reporte no coincidía con el período
real de los datos]

### Fuentes sin publicación a la fecha de esta corrida
[cuáles de las 5 no tenían el informe del mes disponible]
```
