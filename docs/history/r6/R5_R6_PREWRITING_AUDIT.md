# R5 y R6: auditoria tecnica antes de redactar

No se ha editado el articulo ni la memoria congelada de Overleaf. Esta
nota registra trabajo tecnico; no es texto candidato para el paper.

## Trabajo realizado en esta ampliacion

1. Pipeline seleccionado: real_circuit_recovery.py construye la aritmetica
   compacta R5, propaga compuertas X/CX/CCX/MCX reales, aplica IQFT mediante
   FFT exacta y usa recuperacion por candidatos verificados y gcd. No llama
   a factorizacion. La CLI historica sparse_order_finding.py conserva su
   certificador de referencia; no confundir ambos puntos de entrada.
2. Registro elegido sin r: Q>B**2 mediante la cota de Hasse.
3. Cinco casos completos: todos los k en [0,Q), control conservado y trabajo
   limpio despues de cada suma. Comparacion clasica independiente posterior
   a la propagacion y coincidencia con la distribucion ideal independiente.
4. Cache exacta de simulacion: cada transicion se obtiene de las compuertas
   reales antes de reutilizarse. No contiene resultados de una suma clasica
   ni introduce lookup en sintesis. La familia X es una permutacion sin
   fases; verificar sus imagenes de base preserva la extension coherente
   en el subespacio de entrada inicializado. No se simula un vector denso
   de 2**237 amplitudes ni ruido fisico.
5. Tabla tecnica regenerada: validated_recovery_resources.csv, con exactos
   de instrucciones de alto nivel, CCX segun cadena limpia, IQFT ideal y
   memoria. audit_recovery_resources.py coteja conteos y memoria del modelo
   contra los circuitos efectivamente construidos para los cinco casos.
6. Ensayo ideal ampliado: 1000 ecuaciones distintas, diez primos, 100
   repeticiones por instancia. Conserva muestras, parametros, referencias,
   intervalos por instancia y desgloses por p, paridad y tipo de orden.
7. Suite R6 completa: 35 pruebas pasaron. Los chequeos numericos adicionales
   de JSON/NPZ y los cinco cotejos del script de recursos tambien pasaron.

## Validacion funcional real y recursos

| p | P | Orden de referencia | Q | Qubits con pool MCX | CCX aritmetica |
| --- | --- | --- | --- | --- | --- |
| 5 | (0,1) | 9 | 128 | 136 | 10172230 |
| 7 | (3,0) | 2 | 256 | 137 | 1187227 |
| 7 | (0,1) | 3 | 256 | 137 | 9498696 |
| 11 | (10,3) | 7 | 512 | 183 | 33090651 |
| 29 | (6,7) | 5 | 2048 | 237 | 92752247 |

Se propagan redes de alto nivel reales. Los conteos CCX se obtienen de
sus perfiles reales mediante la descomposicion exacta probada, sin
materializar o ejecutar una red de 92 millones de CCX. La IQFT se aplica
en forma ideal y su convencion se comprueba contra Qiskit en pruebas.
Una sola entrada de order finding no representa todos los posibles puntos
iniciales del sumador: aqui empieza en O. Los contratos generales y casos
invalidos tambien tienen pruebas previas independientes en R5.

Para p29,m11, el circuito completo cuenta 92776612 instrucciones en la
base mixta X,CX,CCX,H,CP(theta), 11 mediciones y 237 qubits logicos. Esto
NO es profundidad, T-count, tiempo, qubits fisicos o ejecucion hardware.
Los 443 shots de la cota conservadora no se ejecutaron como tal; se
evaluaron presupuestos hasta 64, con 100 repeticiones por caso real.

## Ampliacion ideal: resultados descriptivos

Primos: 11,17,23,29,41,47,59,67,83,101. Cien curvas por primo, un punto
finito por curva, cien repeticiones independientes por instancia, semilla
429931. Ordenes de referencia entre 2 y 119. No son tamanos criptograficos.
Distintas ecuaciones no significan distintas clases de isomorfismo.

| Shots | Exactos / 100000 | Multiplo no minimo | Sin candidato | Tasa exacta |
| --- | --- | --- | --- | --- |
| 1 | 59292 | 5 | 40703 | 59.292% |
| 2 | 78732 | 3 | 21265 | 78.732% |
| 4 | 92567 | 2 | 7431 | 92.567% |
| 8 | 98706 | 3 | 1291 | 98.706% |
| 16 | 99948 | 0 | 52 | 99.948% |
| 32 | 100000 | 0 | 0 | 100% observado |
| 64 | 100000 | 0 | 0 | 100% observado |

Con 8 shots: ordenes primos 99.962%, compuestos 98.062%; ordenes pares
97.316%, impares 99.943%. Son comparaciones descriptivas, no efectos
causales ni una prueba de superioridad. El peor porcentaje por instancia
fue 84% con 8 shots y 96% con 16. El 100% observado no garantiza exito
universal. Entre presupuestos se usan prefijos de las mismas mediciones.

El ensayo ampliado solo evalua posprocesamiento con una distribucion
ideal conocida por el simulador, no 1000 circuitos aritmeticos reales.
La recuperacion nunca recibe los ordenes de referencia.

## Atribucion y comparacion de modelos

La memoria R5 ya identifica fundamento publicado y construcciones locales:
Proos-Zalka para el antecedente ECDLP/aritmetica reversible; Roetteler para
aritmetica y suma controlada; Cheung-Mosca para posicionamiento de grupos,
no un componente ejecutado. El inversor local usa cocientes euclideos,
no la implementacion binaria de Kaliski de Roetteler. No hereda sus costes.

Roetteler et al., seccion 5, distinguen la estimacion de una suma controlada
(224*log2(n)+2045)*n**2 del total ECDLP multiplicado por 2n. Esas cifras
incluyen ajuste/interpolacion y corresponden a sus circuitos, no son una
formula exacta para nuestras instancias pequenas. Fuente primaria:
https://arxiv.org/pdf/1706.06752 . No convertir el total ECDLP en coste de
una llamada local a kP ni extrapolar su regresion al campo p29 para reclamar
una mejora. La presente referencia prioriza contratos comprobables, no
un avance independiente demostrado sobre esos circuitos.

## Pendientes reales antes de redactar y declarar atendidas R5/R6

- Falta el ZIP ACTUAL del articulo: no hay fuentes del manuscrito disponibles
  en sources/. Se solicito al usuario. Necesario para auditar su definicion
  de C, Ec. (6), Algoritmo 1, Remark 1, Tabla I y apendices, sin editarlos.
- Cotejar las formulas vigentes y cerrar el conjunto numerico que reemplaza
  o conserva cada columna de la Tabla I. El CSV nuevo NO se declara un
  reemplazo automatico de una tabla que no se ha inspeccionado.
- Comprobar en el articulo si R6 promete costes del protocolo de firmas
  completo, o del componente order finding. Si promete el completo, sumar
  sus pasos clasicos especificos; esta nota no presupone cuales son.
- Revisar que toda comparacion use la misma unidad y el mismo alcance.
  Baselines clasicos y posicionamiento global pertenecen tambien a R7/R8;
  no deben darse por resueltos con esta validacion aritmetica.

No son objetivos pendientes de esta version: simulacion de un estado denso,
hardware, CUDA-Q, circuitos optimos o certificacion determinista. Son
exclusiones explicitas del modelo acordado, no resultados implicitos.
La construccion/sintesis clasica offline no se ha cronometrado ni tiene
una cota en bits auditada; no usar las cotas online como tiempo completo
de compilacion y ejecucion. No se ha actualizado el snapshot de la memoria.

## Reproduccion

Desde output/r6, con Anaconda y opciones -s -B:

    python -s -B -m unittest discover -v
    python -s -B real_circuit_recovery.py
    python -s -B audit_recovery_resources.py
    python -s -B random_curve_pilot.py --per-prime 100 --trials 100 --seed 429931 --primes 11 17 23 29 41 47 59 67 83 101 --output expanded_curve_validation.json

Resultados reales: real_circuit_recovery.json/.npz.
Resultados ideales ampliados: expanded_curve_validation.json/.npz.
CSV: validated_recovery_resources.csv.
