# BESS-Chile-Report

Repo fuente de verdad para el agente Capacidad BESS Chile: capacidad instalada (MW/MWh) de BESS y matriz eléctrica chilena, actualizada mensualmente a partir de 5 fuentes públicas.

Este repo es parte del sistema de agentes de PM BESS LATAM (ver Project "Diseño de Agentes" para la arquitectura general y el Registro de Agentes completo).

Qué hay acá
Archivo	Qué es
Informacion_reportes_Mensuales.xlsx	Archivo oficial, único activo (sin fecha en el nombre). Dos hojas: BESS (capacidad en operación/pruebas/construcción, MW y MWh, más la serie de evolución acumulada) y Energy Matrix (capacidad por tecnología, tabla mensual + resumen con gráfico de torta). Contiene los 2 gráficos nativos de Excel que usa el reporte PPT.
CLAUDE.md	Instrucciones que lee la Claude Code Routine en cada corrida mensual: qué fuentes scrapear, cómo mapear cada dato a su celda exacta, y qué reglas no negociables seguir (ver abajo).
/historial/	Copias fechadas (AAAAMMDD_Informacion_reportes_Mensuales.xlsx) de cada corrida, para trazabilidad. No se edita a mano.
Qué NO hay acá

El reporte PowerPoint ("BYD Chile Market Report") nunca se sube a este repo — es confidencial. Se arma en una sesión de Chat aparte, manual, usando este xlsx ya mergeado como fuente de datos. Ver Project "Capacidad BESS Chile" (Chat) para esas instrucciones.

Cómo funciona la actualización mensual
Claude Code Routine (mensual, sin supervisión)
  → scrapea las 5 fuentes (ver CLAUDE.md)
  → verifica el período real de cada informe (no confía en el nombre del mes)
  → actualiza Informacion_reportes_Mensuales.xlsx directo en su rama
  → abre PR con: archivo editado + changelog + copia en /historial/
  → NUNCA mergea su propio PR

Vos
  → revisás el PR (acá o en el Chat de este Project)
  → mergeás si está bien

Las 5 fuentes:

ACERA — Boletín Estadísticas
Ministerio de Energía — Reporte de Proyectos
Coordinador Eléctrico Nacional — Informe Mensual
Generadoras.cl — Boletines Mensuales
Energía Abierta — Reporte mensual del sector energético

Detalle completo de qué celda alimenta cada fuente, y las reglas no negociables (nunca inventar un período, nunca rellenar un hueco con estimación propia, nunca mezclar categorías de distintas fuentes) están en CLAUDE.md — es la referencia autoritativa, este README es solo el mapa de orientación rápida.

Antes de activar el Schedule

Este repo se probó primero con corridas manuales acotadas (meses ya transcurridos, sin mergear) antes de programar la Routine mensual automática. Si vas a reactivar o clonar este patrón para otro país o dominio, seguí el mismo orden: piloto manual acotado → piloto manual completo → recién ahí Schedule.

Estado

Ver Registro de Agentes en el Project "Diseño de Agentes" para el estado actual (piloto / validado / en producción) y última fecha de corrida.
