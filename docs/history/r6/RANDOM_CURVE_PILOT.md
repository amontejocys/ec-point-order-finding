# Piloto de recuperacion probabilistica

## Alcance

Este experimento evalua el posprocesamiento con mediciones de order finding
ideal y sin ruido. NO construye ni ejecuta los circuitos de aritmetica R5.
No mide rendimiento fisico, ventaja cuantica, complejidad asintotica ni
superioridad sobre Proos-Zalka, Roetteler o Ekera. El objetivo del paper
permanece en el metodo hibrido integrado; este es un ensayo de su componente
de recuperacion, separado de la validacion de compuertas reales.

## Protocolo fijado para el piloto

- Primos p = 11, 17, 23, 29, 41; 20 curvas por primo, 100 instancias.
- Coeficientes (a,b) uniformes, rechazando curvas singulares y pares ya
  elegidos para ese p. Distintas ecuaciones NO significan clases de
  isomorfismo distintas. El muestreo no es uniforme sobre esas clases.
- Un punto finito uniforme por curva, elegido de la enumeracion de sus
  puntos. No se seleccionaron instancias por rendimiento observado.
- Orden de referencia por sumas sucesivas con reference_add/reference_order,
  una implementacion de evaluacion separada de la usada en recuperacion.
- Q > B**2, B = p+1+isqrt(4*p), elegido sin usar el orden verdadero.
- 100 repeticiones por instancia, cada una con 64 resultados independientes.
- Presupuestos prefijados T = 1,2,4,8,16,32,64, evaluados sobre prefijos de
  la misma secuencia. Los resultados ENTRE presupuestos estan correlacionados:
  no son 70.000 repeticiones independientes.
- Semilla 20261008; flujos separados para curvas y mediciones. Versiones de
  Python/NumPy registradas en JSON; mediciones crudas en NPZ.

La enumeracion clasica y el orden verdadero pertenecen al banco de prueba,
no al algoritmo propuesto ni a su coste de ejecucion. El simulador ideal
usa el orden verdadero para generar mediciones; recover_prefixes no lo
recibe, ni accede a ese dato. Por eso no es una simulacion del circuito
aritmetico construido, sino del modelo ideal de sus mediciones.

## Distribucion ideal y recuperacion

Para Q = L*r+t, hay t clases periodicas con L+1 entradas y r-t con L.
Despues de IQFT y trazar el registro de salida:

    Pr(y) = [t*|S_(L+1)(y)|**2 + (r-t)*|S_L(y)|**2] / Q**2
    S_n(y) = sum_(j=0..n-1) exp(-2*pi*i*j*r*y/Q).

ideal_probabilities evalua la suma geometrica mediante sinc para evitar
singularidades numericas. La formula se deriva del estado periodico y su
transformada de Fourier, no es un nuevo algoritmo. Contexto primario:
Shor, seccion 5, https://arxiv.org/abs/quant-ph/9508027 .
Las pruebas la comparan con una FFT independiente que conserva etiquetas
de salida ortogonales, para Q = 8,16,32,64 y todos los r entre 1 y Q.

recover_prefixes recibe mediciones, curva, punto y Q. Obtiene denominadores
de convergentes, verifica dP=O y acumula su gcd. No factoriza ni certifica
minimalidad. La cache entre repeticiones acelera el banco de prueba; NO
debe contarse como ahorro de verificaciones en ejecuciones independientes.

El evaluador clasifica contra la referencia: exacto, multiplo no minimo,
sin candidato. Todas las ejecuciones cuentan en el denominador del porcentaje;
no se descartan las que no produjeron candidato.

## Resultado observado

Cada fila resume 10.000 repeticiones sobre las mismas 100 instancias.

| Mediciones | Orden exacto | Multiplo no minimo | Sin candidato | Tasa exacta |
| --- | --- | --- | --- | --- |
| 1 | 5520 | 0 | 4480 | 55.20% |
| 2 | 7564 | 2 | 2434 | 75.64% |
| 4 | 9172 | 1 | 827 | 91.72% |
| 8 | 9857 | 1 | 142 | 98.57% |
| 16 | 9987 | 0 | 13 | 99.87% |
| 32 | 10000 | 0 | 0 | 100% observado |
| 64 | 10000 | 0 | 0 | 100% observado |

El peor porcentaje por instancia fue 89% con 8 mediciones y 97% con 16.
El agregado no debe ocultar esa variacion. No se infiere una garantia
universal a partir del 100% observado, ni extensibilidad experimental a
tamanos criptograficos. Se registran intervalos Wilson aproximados al 95%
para cada instancia fija y presupuesto, no un intervalo binomial agrupado
que asuma una probabilidad de exito comun a todas las curvas. No son
intervalos simultaneos corregidos por comparaciones multiples.

## Artefactos y reproduccion

- random_curve_pilot.py: generador, referencia independiente, distribucion,
  recuperacion y reporte.
- test_random_curve_pilot.py: cuatro pruebas nuevas; junto con las seis
  de test_factor_free_recovery, diez pruebas pasaron.
- random_curve_pilot.json: protocolo, versiones, parametros, referencias,
  resultados por instancia y resumen.
- random_curve_pilot.npz: mediciones, forma (100,100,64), en el orden de las
  instancias del JSON. No contiene estados cuanticos ni una tabla del oraculo.

Desde output/r6, en el entorno de Anaconda de esta maquina:

    python -s -B -m unittest test_random_curve_pilot test_factor_free_recovery -v
    python -s -B random_curve_pilot.py

## Antes de incorporar al paper

Este piloto no cambia el paper ni la memoria de Overleaf. Primero revisar
el protocolo, ampliar tamanos/repeticiones y casos dirigidos con ordenes
compuestos, separar resultados por instancia/tamano/tipo de orden y definir
si se necesitan comparadores. Una ampliacion exige ampliar los parametros
del generador; la CLI actual limita a 20 curvas por primo para este piloto.
La validacion real del circuito debe permanecer como experimento distinto.
La garantia teorica y el coste de las repeticiones se analizan aparte de
estos porcentajes observados. No se declara concluido R6.
