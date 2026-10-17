# Recuperacion sin factorizar: prototipo, no sustitucion de R5

## Problema que separa este paso

En R5, recovered_orders verifica candidatos d, factoriza d por division
de prueba y elimina factores para certificar el orden minimo. Ese ultimo
paso no tiene una garantia polinomica en el numero de bits.

factor_free_recovery.py conserva verified_candidates, pero acumula el
maximo comun divisor de todos los candidatos verificados. No llama a
reduce_order_multiple ni a prime_factors_trial. No modifica la aritmetica
cuantica, la memoria de Overleaf ni el manuscrito.

## Garantia algebraica y su limite

Sea r el orden desconocido de un punto valido P. Si dP = O, escribir
d = qr + s, con 0 <= s < r, da sP = O. La minimalidad de r obliga s = 0.
Por tanto, todo candidato positivo verificado es un multiplo de r.

Si d1 = r*u y d2 = r*v, entonces:

    gcd(d1, d2) = r*gcd(u, v).

El acumulador sigue siendo un multiplo positivo de r y sigue anulando P.
Tambien puede demostrarse con Bezout: g = a*d1 + b*d2 implica gP = O.
Al aceptar r alguna vez, el acumulador se vuelve r y ya no puede cambiar.
Tambien puede llegar a r sin aceptar r directamente: 10 y 15 dan 5.

Pero aceptar solo 10, o repetir 10 muchas veces, NO prueba que r = 10.
Estabilidad del acumulador tampoco certifica minimalidad. El retorno es
verified_period, no certified_order. minimality_certified queda False
incluso cuando una referencia externa del test sabe que el resultado es r.
No existe una confianza numerica implicita ni un criterio de parada por
estabilidad. Un prefijo sin candidatos retorna None.

## Conexion con order finding y resolucion

Shor, seccion 5, explica la aproximacion s/r mediante fracciones continuas:
un resultado suficientemente cercano y gcd(s,r)=1 permite recuperar r.
Su analisis obtiene una probabilidad asintotica de exito de orden al menos
1/log(log(r)), bajo las condiciones de resolucion de ese algoritmo.
La extension de esa condicion a f(k)=kP usa su periodo minimo r y una
codificacion inyectiva de los puntos; no necesita que r sea par.

Para una cota desconocida r <= B, elegir Q > B**2 permite que el resultado
mas cercano a s/r satisfaga error <= 1/(2Q) < 1/(2r**2). Si s/r esta
reducida, la propiedad clasica de fracciones continuas asegura que aparece
como convergente. Elegir Q asi no garantiza que toda medicion sea buena.

El limite de Hasse permite B = p + 1 + isqrt(4*p), sin enumerar puntos ni
conocer r. uniform_register_size usa m = bit_length(B**2), Q = 2**m.
Para p=29 da B=40, m=11, Q=2048. Q=32 sigue siendo el experimento pequeno
previo; NO se transforma en garantia uniforme de orden desconocido. No se
ha construido ni simulado aqui el circuito m=11, y sus recursos deben
recalcularse si se decide usarlo.

Si cada shot independiente tiene probabilidad al menos alpha de aceptar
r, el fracaso del acumulador para obtener r tras T shots es como maximo
(1-alpha)**T. Puede ser menor porque distintos multiplos tambien pueden
dar r. Esta es una formula condicional, no una confianza calculada para
Q=32 ni una cota finita explicita derivada en este prototipo.

## Coste y atribucion

Los convergentes de y/Q son O(m) y sus enteros tienen O(m) bits. Cada
verificacion dP usa O(log(d)) operaciones de grupo por double-and-add;
las verificaciones se limitan a d <= B. El gcd es aritmetica clasica
polinomica en los bits. Asi, el trabajo por shot es polinomico en m y
log(p), suponiendo aritmetica clasica de campo polinomica. Esto elimina
la division de prueba de ESTE posprocesamiento, no demuestra por si solo
una cota global, una certificacion determinista, ni una ventaja comparativa.

Fuentes primarias:

- Shor: https://arxiv.org/abs/quant-ph/9508027 , seccion 5. Fundamenta
  fracciones continuas, recuperacion probabilistica y grupos generales.
- Ekera: https://arxiv.org/abs/2201.07791 . Analiza estrategias mas fuertes
  de posprocesamiento. NO se ha implementado su algoritmo ni transferido
  su cota de exito a este prototipo.

La acumulacion por gcd de multiplos ya verificados es una eleccion local
con la demostracion elemental anterior; no se presenta como novedad ni
se atribuye como implementacion de Ekera. No debe confundirse con el lcm
de denominadores divisores que Shor discute: son invariantes diferentes.
Proos-Zalka y Roetteler siguen sustentando el contexto de aritmetica
reversible; no se les atribuye este posprocesamiento.

## Validacion reproducible

    python -s -B -m unittest test_factor_free_recovery -v
    python -s -B factor_free_recovery.py

Seis pruebas pasan: ausencia de llamadas a factorizacion; ejemplo 10/15;
casos sin informacion; todos los resultados en tres curvas con ordenes
5, 3 y 2; preservacion de r una vez aceptado; resolucion por cota desconocida
y rechazo de entradas invalidas. Los ordenes conocidos son referencias
de pruebas, nunca entradas del protocolo. Recorrer todos los resultados
en pruebas NO representa mediciones tomadas ni una estimacion de exito.

Pendiente antes de integrar: decidir recuperacion probabilistica o
certificacion determinista, fijar resolucion y presupuesto de shots,
derivar la garantia correspondiente y comparar con posprocesamientos
publicados. R6 no se declara terminado por estas pruebas.
