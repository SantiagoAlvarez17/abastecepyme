# Bitácora de uso de IA — Feature 2: Análisis de impacto

## Sesión 1 — Consulta de impacto con recorrido BFS propio (rama `feature/analisis-impacto`, Equipo5)

- **Herramienta:** Claude (chat de claude.ai).
- **Fecha:** 2026-10-27

[PASA ] Consulta sin datos: impacto en un catálogo vacío
        esperado: 404 ERR_ELEMENT_NOT_FOUND
        obtenido: 404 ERR_ELEMENT_NOT_FOUND

[PASA ] Preparación: 9 elementos y 8 dependencias
        esperado: todos creados con 201
        obtenido: 9 elementos, 8 dependencias

[PASA ] Normal: si falla Molinos SA, se afecta toda la cadena que lo usa
        esperado: 200 chain, 5 afectados en 3 niveles: {Harina, Levadura} → {Masa madre, Torta} → {Pan}
        obtenido: 200 chain, 5 afectados en 3 niveles: [{'Levadura', 'Harina'}, {'Masa madre', 'Torta'}, {'Pan'}]

[PASA ] Normal: cada elemento afectado trae su ruta y la frase del negocio
        esperado: ruta que empieza en Molinos SA y termina en Pan (4 nombres); razón 'Para producir Pan necesito Masa madre'
        obtenido: ruta=['Molinos SA', 'Harina', 'Masa madre', 'Pan'], razón='Para producir Pan necesito Masa madre'

[PASA ] Normal: si falta Harina, se afectan Masa madre, Torta y Pan
        esperado: chain, 3 afectados en 2 niveles: {Masa madre, Torta} → {Pan}
        obtenido: chain, 3 afectados en 2 niveles: [{'Masa madre', 'Torta'}, {'Pan'}]

[PASA ] Relación inexistente: la falla de Granja El Roble no alcanza a Pan
        esperado: afecta {Huevos, Torta}; Pan, Masa madre y Panela no aparecen
        obtenido: afectados=['Huevos', 'Torta']

[PASA ] Normal: ¿qué necesita Pan para producirse? (modo requirements)
        esperado: chain, 4 elementos en 3 niveles: {Masa madre} → {Harina, Levadura} → {Molinos SA}
        obtenido: chain, 4 elementos en 3 niveles: [{'Masa madre'}, {'Levadura', 'Harina'}, {'Molinos SA'}]

[PASA ] Sin dependencias: Panela no necesita nada ni nadie la necesita
        esperado: 200 isolated, 0 afectados
        obtenido: 200 isolated, 0 afectados

[PASA ] Sin alcance: si falla Pan no se afecta a nadie (producto final)
        esperado: 200 no_reach, 0 afectados
        obtenido: 200 no_reach, 0 afectados

[PASA ] Sin alcance: Molinos SA no necesita nada para 'producirse' (proveedor)
        esperado: 200 no_reach, 0 elementos
        obtenido: 200 no_reach, 0 elementos

[PASA ] Elemento inexistente: id que no está en el catálogo
        esperado: 404 ERR_ELEMENT_NOT_FOUND
        obtenido: 404 ERR_ELEMENT_NOT_FOUND

[PASA ] Dato inválido: id mal formado
        esperado: 422 ERR_VALIDATION con message
        obtenido: 422 ERR_VALIDATION

[PASA ] Dato inválido: modo de consulta desconocido
        esperado: 422 ERR_VALIDATION con message
        obtenido: 422 ERR_VALIDATION

[PASA ] Ciclo: se registra 'Masa madre necesita Pan' (Pan ya necesitaba Masa madre)
        esperado: 201 (F1 lo guarda; la alerta del ciclo corresponde a F3)
        obtenido: 201

[PASA ] Ciclo: el impacto de Molinos SA termina y no repite elementos
        esperado: 200, 5 afectados sin repetidos
        obtenido: 200, 5 afectados, 5 distintos

[PASA ] Ciclo: el origen no aparece como afectado de sí mismo
        esperado: 200, afectados = [Masa madre] (Pan no se cuenta)
        obtenido: 200, afectados=['Masa madre']

Resultado: 16/16 escenarios pasaron

