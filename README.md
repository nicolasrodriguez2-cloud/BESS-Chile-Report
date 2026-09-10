BESS-Chile-Report

Repo fuente de verdad para el agente Capacidad BESS Chile: capacidad instalada (MW/MWh) de BESS y matriz eléctrica chilena, actualizada mensualmente a partir de 5 fuentes públicas.

Este repo es parte del sistema de agentes de PM BESS LATAM (ver Project "Diseño de Agentes" para la arquitectura general y el Registro de Agentes completo).

Qué hay acá
Archivo/carpeta	Qué es
Información_reportes_Mensuales.xlsx	Archivo oficial, único activo (sin fecha en el nombre). Dos hojas: BESS (capacidad en operación/pruebas/construcción, MW y MWh, más la serie de evolución acumulada) y Energy Matrix (capacidad por tecnología, tabla mensual + resumen con gráfico de torta). Contiene los 2 gráficos nativos de Excel que usa el reporte PPT.
/ACERA/, /E ABIERTA/	PDFs mensuales de las 2 fuentes que sí se scrapean solas — la Routine los archiva acá cada corrida como respaldo/auditoría de qué documento sustenta cada cifra. No son el insumo que la Routine lee (siempre fetchea en vivo), son el registro.
/COORDINADOR/, /MIN ENERGIA/	PDFs mensuales subidos a mano por Nicolás — estas 2 fuentes bloquean el acceso automatizado (una por robots.txt declarado contra ClaudeBot, la otra por WAF de dominio completo — ver CLAUDE.md). La Routine lee de acá, nunca las descarga sola.
/GENERADORAS/	PDFs mensuales — pendiente de confirmar si esta fuente puede pasar a automatizada (ver CLAUDE.md). Mientras tanto se trata igual que Coordinador/Min. Energía.
CLAUDE.md	Instrucciones que lee la Claude Code Routine en cada corrida mensual: qué fuentes scrapear, cómo mapear cada dato a su celda exacta, y qué reglas no negociables seguir. Es la referencia autoritativa — este README es solo el mapa de orientación rápida.
/historial/	Copias fechadas (AAAAMMDD_Información_reportes_Mensuales.xlsx) de cada corrida, para trazabilidad. No se edita a mano.

⚠️ Dos carpetas tienen espacio en el nombre (E ABIERTA, MIN ENERGIA) — tenerlo en cuenta si algún script arma el path a mano. Cada carpeta tiene además un archivo suelto sin extensión (Acera, Coord, Gen, Min, E ABIERTA) de origen no confirmado — pendiente de revisión.

Qué NO hay acá

El reporte PowerPoint ("BYD Chile Market Report") nunca se sube a este repo — es confidencial. Se arma en una sesión de Chat aparte, manual, usando este xlsx ya mergeado como fuente de datos. Ver Project "Capacidad BESS Chile" (Chat) para esas instrucciones.

Cómo funciona la actualización mensual
Claude Code Routine (mensual, sin supervisión)
  → ACERA y E. Abierta: fetch directo por URL + archiva copia en su carpeta
  → Coordinador, Min. Energía (y Generadoras mientras esté pendiente):
    lee el PDF del mes desde su carpeta — nunca intenta bajarlo sola
  → verifica el período real de cada informe (no confía en el nombre del mes)
  → actualiza Información_reportes_Mensuales.xlsx directo en su rama
  → abre PR con: archivo editado + changelog + copia en /historial/
  → NUNCA mergea su propio PR

Vos
  → cada mes, subís a /COORDINADOR/ y /MIN ENERGIA/ el PDF nuevo
    (navegando el sitio como cualquier persona)
  → revisás el PR (acá o en el Chat del Project)
  → mergeás si está bien

Detalle completo de qué celda alimenta cada fuente, el mapeo exacto de las 6 tablas de la hoja BESS, y las reglas no negociables (nunca inventar un período, nunca rellenar un hueco con estimación propia, nunca evadir un bloqueo declarado o técnico) están en CLAUDE.md.

Cómo conectar este repo desde Chat (claude.ai)

No lo agregues como "Project Knowledge" completo — el repo pesa por los PDFs acumulados y esa sincronización falla o se vuelve lenta. En su lugar: subí solo CLAUDE.md como Project Knowledge (es texto, liviano), y activá el conector de GitHub a nivel de cuenta (Settings → Connectors) para este Project — así se trae un archivo puntual cuando se necesita, sin cargar el repo entero.

Antes de activar el Schedule

Este repo se probó primero con corridas manuales acotadas (meses ya transcurridos, sin mergear) antes de programar la Routine mensual automática. Si vas a reactivar o clonar este patrón para otro país o dominio, seguí el mismo orden: piloto manual acotado → piloto manual completo → recién ahí Schedule.

Estado

Ver Registro de Agentes en el Project "Diseño de Agentes" para el estado actual (piloto / validado / en producción) y última fecha de corrida.
