# R6, paso 1: costes de la aritmetica de referencia

Estos archivos auditan output/r5; no modifican sus circuitos ni el snapshot
de la memoria Overleaf. No describen un circuito optimizado publicado.

## Modelo de coste

Una instruccion X, CX, CCX o MCX cuenta como una unidad, independientemente
de su numero de controles. La inversion de un bloque mantiene su numero
de instrucciones; agregar controles a esas instrucciones tampoco cambia
este conteo. No son Toffolis sintetizadas, profundidad ni costes fisicos.

## Formulas exactas y funciones auditadas

Sea B(w,a) el numero de instrucciones de binary_add_constant(w,a), con
a normalizado modulo 2**w. Cada bit activo j cuesta w-j instrucciones:

    B(w,a) = suma_j bit_j(a mod 2**w) * (w-j)
    B(w,a) <= w*(w+1)/2

Esto sale de los bucles shift/target de binary_add_constant.py.

Para less_than_constant(w,L), se copia y descopia el registro (2*w CNOT),
se aplica una resta y su inversa y se transfiere un indicador:

    T(w,L) = 2*w + 2*B(w+1,-L) + 1

Para modular_add_constant(w,p,a), normalizando a modulo p:

    A(w,p,a) = 2*T(w,p)
             + B(w+1,a)
             + T(w+1,p)
             + 1
             + B(w+1,-p)
             + T(w+1,a)

Los terminos son, en orden: las dos comprobaciones de validez, suma,
comparacion para reduccion, CNOT valid->reduce, resta de p y limpieza
del indicador de reduccion. Incluyen todas las instrucciones de limpieza.

modular_add_register usa una suma constante controlada por cada bit j:

    R(w,p) = suma_j A(w,p,2**j mod p), omitiendo constantes cero

modular_multiply_accumulate usa una por cada par i,j:

    M(w,p) = suma_i,j A(w,p,2**(i+j) mod p), omitiendo ceros

modular_square_accumulate usa diagonales y pares distintos:

    S(w,p) = suma_i A(w,p,2**(2*i) mod p)
           + suma_i<j A(w,p,2**(i+j+1) mod p), omitiendo ceros

modular_cube_accumulate calcula, usa y descalcula el cuadrado:

    U(w,p) = 2*S(w,p) + M(w,p)

## Cotas superiores de esta implementacion

- Suma binaria constante: O(w**2).
- Comparacion con constante: O(w**2).
- Suma modular constante: O(w**2).
- Suma modular de registro: O(w**3).
- Producto, cuadrado y cubo modular: O(w**4).
- Comparacion entre registros y paso de division: O(w**3).
- Division completa y salida de solo cociente: O(w**4).
- Inversor compacto con 2*w+1 rondas: O(w**5).
- Qubits logicos del inversor compacto: O(w**2).

Son cotas superiores conservadoras derivadas del codigo, no ajustes a una
tabla de ejemplos ni afirmaciones Theta. Algunas constantes cuestan menos.
No deben aplicarse a implementaciones distintas de esas funciones.
La integracion en la suma completa de puntos se documenta en el paso 3.
No se ha fijado aun un modelo de descomposicion de MCX; ese estudio puede cambiar
las cotas de coste y de memoria en una base de compuertas distinta.

## Paso 2: division e inversor compacto

Definimos E(w,a)=2*(w-popcount(a))+1, el conteo de equality_constant.
Definimos S(w,v)=suma_j=0..w-1 B(v,-2**j), el conteo de resta de un
registro w-bit sobre un destino v-bit. Agregar controles no cambia este
conteo de instrucciones, aunque si cambia su futura sintesis.

Para less_than_register y division_reduce_step:

    L(w) = 2*w + 2*S(w,w+1) + 1
    D_step(w) = L(w) + 1 + S(w,w)

binary_divide conserva restos de w+1 bits, por lo que invoca D_step(w+1),
no D_step(w). Sus CNOT de copia son w**2: w copias de bits del dividendo
mas w*(w-1) copias de restos anteriores.

    D_compute(w) = E(w,0) + 1 + w**2 + w*D_step(w+1)
    D(w) = 2*D_compute(w) + 2*w
    Q(w) = 2*D_compute(w) + w

D es binary_divide y Q es binary_quotient. La diferencia es solo la
transferencia del resto a un registro de salida de w bits. No se elimina
el historial interno: Q conserva w**2+6*w+4 qubits en total.

Para modular_inverse_inplace, cada ronda contiene:

    Actividad:       E(w,0)+1
    Cociente:        Q(w)
    Resta binaria:   H(w)=suma_i,j con i+j<w B(w,-2**(i+j))
    Resta modular:   M(w,p)
    Dos SWAP de registros controlados: 6*w

Si J es la suma de esos cinco terminos:

    rondas = 2*w+1
    inicializacion = popcount(p)+w+1
    predicados finales = T(w,p)+E(w,0)+1+E(w,1)+E(w,0)
    compute = inicializacion + rondas*J + predicados finales
    I_compact(w,p) = 2*compute + w

El factor 2 cuenta calcular y descalcular. El ultimo w transfiere los
bits del inverso al destino. El numero de rondas no disminuye aunque una
entrada llegue a resto cero temprano: las rondas restantes estan en la
red y quedan inactivas coherentemente para esa entrada.

### Desglose verificado para w=5, p=29

    Actividad por ronda:             12
    Cociente por ronda:            2439
    Resta binaria por ronda:         70
    Resta modular por ronda:       4365
    Intercambios por ronda:          30
    Total por ronda:              6916
    Numero de rondas:                11
    Inicializacion:                 10
    Predicados finales:             67
    Calculo hacia adelante:      76153
    Transferencia de salida:         5
    Total con limpieza:         152311

La derivacion usa O(w**3) para la resta/comparacion de registros;
O(w) pasos dan O(w**4) para division. Cociente, resta de producto binario
y producto modular tienen cota O(w**4) por ronda. O(w) rondas dan la cota
O(w**5) del inversor completo. Son derivaciones de los bucles actuales,
no regresiones a partir de los ejemplos ni costes trasladados de otro paper.

### Memoria del inversor: por que sigue siendo cuadratica

El cuarteto r0,r1,c0,c1 se comparte, pero no desaparece todo el historial:

    Entrada y destino:                  2*w
    Cuarteto euclideo:                  4*w
    Cocientes retenidos:               (2*w+1)*w
    Indicadores de actividad:          2*w+1
    Trabajo del cociente:              w**2+3*w+4
    Trabajo del producto modular:      w+5
    Predicados finales:                4
    Total:                             3*w**2+13*w+14

Con w=5, esto da 154 qubits y coincide con circuit.num_qubits. Son todos
los qubits del inversor aislado, incluidos entrada y destino. No es la
memoria del circuito completo de order finding ni una cota fisica.

## Paso 3: suma de puntos y evaluacion escalar compacta

Las formulas siguientes describen evaluator_variant="compact" e
inverse_variant="compact". Excluyen precomputacion clasica, Hadamard,
preparacion de identidad, QFT, medicion, posprocesamiento y shots. La
memoria excluye bits clasicos. Son costes de la referencia, no de otros
circuitos publicados ni del simulador clasico que recorre 2**m entradas.

### Validadores y selectores de casos

Sea C el conteo de curve_residual_accumulate: cuadrado, cubo, las sumas
del termino -a*x y la suma -b. finite_curve_check calcula y descalcula
el residuo y los predicados de validez:

    F = 4*T(w,p) + 2*C + 2*E(w,0) + 1
    V = 2*F + 4*w + 4

V corresponde a point_encoding_check. point_addition_cases usa V y tres
igualdades con O,A,-A, calcula los selectores y descalcula los predicados:

    s = 2*w+1
    K(A) = 2*(V + E(s,enc(O)) + E(s,enc(A)) + E(s,enc(-A))) + 12

C,F,V,K tienen cota superior O(w**4). Una rama no se elimina del conteo
porque no se active para una entrada particular: sus controles y bloques
pertenecen a la red coherente.

### Coordenadas ordinarias compartidas

ordinary_point_sum_shared calcula las dos coordenadas antes de limpiar.
Su red hacia adelante contiene 3*w CNOT de copia, dos restas constantes
-u, una -v, un inversor, dos productos, un cuadrado y tres restas de registro:

    O_compute(A) = 3*w + 2*A(w,p,-u) + A(w,p,-v)
                 + I_compact(w,p) + 2*M(w,p) + S(w,p) + 3*R(w,p)
    O(A) = 2*O_compute(A) + 2*w

A(w,p,a) significa el coste del sumador; A=(u,v) en O(A) es el punto.
El factor 2 cuenta la limpieza y el ultimo 2*w transfiere las coordenadas.
La cota del inversor domina: O(A)=O(w**5).

### Evaluador total y actualizacion controlada

point_sum_evaluator_compact calcula los selectores, agrega las ramas
especiales y ordinaria, copia entradas invalidas y descalcula los selectores:

    Z(A) = popcount(enc(A)) + 1 + popcount(enc(2A))
    G_eval(A) = 2*K(A) + O(A) + Z(A) + 2*E(4,0) + s

point_add_inplace evalua A, intercambia s pares y evalua -A para borrar
el punto anterior. controlled_point_add agrega controles a toda la red;
cada SWAP se convierte en tres CCX:

    G_add(A) = G_eval(A) + G_eval(-A) + 3*s

G_eval y G_add tienen cota superior O(w**5). Agregar un control conserva
el conteo de alto nivel, no el coste de una futura descomposicion MCX.

Para p=29,a=0,b=7,A=(6,7):

    G_eval(A)                       = 533372
    G_eval(-A)                      = 533394
    Intercambios controlados        = 33
    G_add(A)                        = 1066799
    Qubits del sumador controlado   = 217
    De ellos: control 1, punto 11, trabajo limpio 205

### Cadena escalar y reutilizacion de memoria

EllipticOrderFinding.scalar_update agrega un bloque para cada constante
P_j=2**j*P no identidad. La cache evita reconstruir constantes repetidas,
pero cada llamada contribuye nuevamente al coste del circuito:

    G_scalar = suma_j:P_j!=O G_add(P_j)
    G_scalar = O(m*w**5)

Si m se elige proporcional a w, la cota es O(w**6) para esta referencia.
Esto no debe confundirse con el coste de un backend optimizado hipotetico:
ese backend requiere construccion y justificacion si se usa en un analisis.
En la instancia p=29,m=5, los cinco conteos son:

    1066799, 1066893, 1066799, 1066893, 1066799
    Total: 5334183

La variacion depende de constantes y patrones binarios. Para la memoria,
el trabajo ordinario I_qubits+6*w+5 supera al de casos (3*w+13). Por tanto:

    Q_eval = 3*w**2+23*w+26
    Q_controlled_add = Q_eval+1
    Q_scalar = m+Q_controlled_add-1 = m+3*w**2+23*w+26

La memoria es O(m+w**2), no m veces la memoria del sumador. Para w=m=5:

    Escalar: 5
    Punto: 11
    Trabajo reutilizado: 205
    Total: 221

La X que prepara O agrega una instruccion a G_scalar sin agregar qubits.
Hadamard y QFT conservan esos cables, pero deben agregarse al conteo de
operaciones en una base definida. El analisis completo debe separar tambien
posprocesamiento y numero de ejecuciones; no se ha cerrado R6 con esta tabla.

## Estado de validacion del contador

Doce pruebas del contador pasan. Confrontan division para anchuras 1..6,
e inversor para (w,p)=(2,3),(3,5),(4,9),(5,29), ademas de los bloques
aritmeticos del paso 1. Se comprueba el conteo de instrucciones y memoria,
no se vuelve a afirmar validacion funcional completa a partir de esos
conteos. No se ha modificado ningun circuito de output/r5 ni la memoria
Overleaf que el usuario esta revisando.

En el paso 3 se reconstruyo la cadena pequena sobre F5 y se confrontaron
sus sumadores, instrucciones y qubits con el modelo. Se reconstruyeron
validadores sobre F5 y F29 y evaluadores pequenos, incluido un punto de
orden dos. Para la cadena grande F29 se contrasto el modelo con los
registros de ejecucion anteriores; no se construyo ni simulo nuevamente
completa. La prueba distingue esa regresion historica de una nueva corrida.

## Procedencia

Las formulas de conteo son una derivacion del codigo local, no una formula
copiada de Proos-Zalka o Roetteler. La expansion binaria escolar del producto
y las operaciones de campo no se presentan como ideas nuevas. La memoria
R5 detalla el marco publicado y distingue su aritmetica de esta referencia.
El contador analitico no construye ni modifica ninguna compuerta.

## Paso 4: una base explicita X, CX, CCX para la aritmetica

mcx_basis.py implementa una cadena exacta de AND con Toffolis completas,
no compuertas de fase relativa. Es una sintesis de referencia, no una
optimizacion nueva ni un minimo demostrado. El uso de redes para controles
multiples tiene antecedentes en Barenco y colaboradores, "Elementary gates
for quantum computation", Phys. Rev. A 52, 3457 (1995):
https://arxiv.org/abs/quant-ph/9503016

La formula concreta siguiente se demuestra a partir de nuestra cadena;
no se atribuye a una figura o lema especifico no verificado de esa fuente.

### Como se descompone una MCX de k controles

Si k=0, se usa X. Si k=1, se usa CX. Si k=2, se usa CCX. Para k>=3,
append_clean_mcx calcula AND parciales en k-2 qubits limpios, aplica una
CCX final al objetivo y revierte las AND parciales:

    Calcular AND parciales: k-2 CCX
    Cambiar objetivo:      1 CCX
    Descalcular:           k-2 CCX
    Total:                 2*k-3 CCX

Por ejemplo, con tres controles c0,c1,c2:

    w <- w XOR (c0 AND c1), empezando w=0
    t <- t XOR (w AND c2)
    w <- w XOR (c0 AND c1), terminando w=0

El objetivo cambia exactamente si todos los controles son uno; las AND
parciales se limpian y las Toffolis completas no agregan fases. La prueba
por induccion extiende la construccion a cualquier k. Los auxiliares deben
empezar en cero; el contrato no promete funcionar con auxiliares sucios.

### Histograma de controles y conteo exacto

control_profile(circuit) inspecciona cada instruccion REAL del bloque plano
de R5 y registra h[k], la cantidad de compuertas con k controles. Rechaza
Hadamard, rotaciones, mediciones y bloques no expandidos de otras familias.

    X    = h[0]
    CX   = h[1]
    CCX  = suma_k>=2 h[k]*(2*k-3)
    Pool limpio dedicado = max(0,k_max-2)

basis_resources aplica esas reglas. lower_x_family puede materializar la
expansion para circuitos pequenos. No se materializa la cadena grande:
audit_mcx_basis.py reconstruye las definiciones aritmeticas originales y
calcula su histograma, confrontandolo con el contador analitico del paso 3.
Es un conteo exacto para esta sintesis y no una transpilacion programada
con routing, conectividad, planificacion de profundidad o correccion de error.

Se reserva un pool nuevo que se comparte entre todas las expansiones MCX.
No se asume que los 205 auxiliares del circuito original esten disponibles
a mitad de un bloque: pueden contener informacion. La limpieza de cada
cadena permite reutilizar el pool antes de la siguiente instruccion.

### Alcance y pruebas

Cuatro pruebas verifican: estados complejos y reversibilidad para 0..7
controles, reutilizacion del pool con distintas aridades, rechazo de puertas
fuera de la base y propagacion exacta de entradas de base seleccionadas
para 8,13,32 controles. Los estados complejos comparan amplitudes, no solo
probabilidades, y comprueban todo el registro de trabajo en cero al salir.

La base X,CX,CCX cubre la ARITMETICA. No implementa la QFT, que necesita
Hadamard y fases controladas. Tampoco se reporta aun T-count, profundidad,
tiempo de hardware o qubits fisicos. Comparar el CCX-count con una fuente
requiere ademas alinear el problema (order finding o ECDLP), parametros,
numero de sumas, tratamiento de excepciones y alcance de los conteos.
Usar una misma unidad es necesario pero no basta para afirmar una mejora.

Los controles maximos de nuestra red crecen como O(w); la cadena cuesta
O(k) CCX por MCX. Una cota superior conservadora tras esta sintesis es
O(m*w**6) CCX para la aritmetica escalar, frente a O(m*w**5) instrucciones
de alto nivel. No se presenta como una cota ajustada ni como una regresion.
El pool extra tiene O(w) qubits y mantiene O(m+w**2) qubits en total.

Desde output/r6:

    python -s -B -m unittest test_mcx_basis -v
    python -s -B audit_mcx_basis.py --output p29_ccx_resources.json

El segundo comando puede tardar minutos. Su JSON identifica el modelo,
las exclusiones, el histograma real y los conteos por cada suma. El metodo
no utiliza el orden del punto ni enumera kP para sintetizar compuertas.

### Auditoria real p=29,Q=32 registrada

Se reconstruyeron los cuatro sumadores distintos y se inspeccionaron las
cinco llamadas reales de scalar_update. El archivo p29_ccx_resources.json
registra el histograma y los resultados de esta nueva corrida:

    Instrucciones originales de alto nivel: 5334183
    Controles maximos en una instruccion:   12
    X en la aritmetica controlada:           0
    CX tras la expansion:                  11024
    CCX tras la expansion:                 42160043
    Total X+CX+CCX:                        42171067
    Pool adicional limpio dedicado:        10 qubits
    Qubits originales:                     221
    Qubits con esta sintesis:               231

Para A=(6,7), una suma controlada aislada se expande a 8431907 CCX y
2192 CX, con 227 qubits (217 originales mas el pool de 10). Las otras
constantes cambian ligeramente el conteo. El pool se reutiliza y no se
asignan diez qubits nuevos a cada una de las cinco sumas.

La cifra 42160043 es el conteo de la expansion exacta definida por nuestras
reglas, aplicada al histograma real. No se materializaron 42 millones de
instrucciones ni se simulo ese circuito expandido completo. La correccion
de la expansion se apoya en la construccion compute/use/uncompute y las
cuatro pruebas de mcx_basis; no se afirma una nueva corrida completa de
amplitudes para p=29. No es un minimo ni una mejora frente a otra sintesis.
La auditoria no cambia los archivos de R5 ni su snapshot Overleaf.

## Paso 5: preparacion, QFT y posprocesamiento separados

complete_resources.py agrega el overhead cuantico al registro real del
paso 4. No reconstruye ni simula otra vez toda la aritmetica grande.
qft_with_cx_swaps inspecciona la definicion real de QFTGate(m).inverse(),
reemplaza cada SWAP por tres CX y preserva el resto. Para la QFT exacta:

    Preparacion de identidad: 1 X
    Superposicion inicial: m H
    IQFT: m H, m*(m-1)/2 CP(theta), floor(m/2) SWAP
    IQFT tras quitar SWAP: 3*floor(m/2) CX en lugar de esos SWAP
    Medicion: m bits, fuera del conteo de compuertas unitarias

La base completa es X,CX,CCX,H,CP(theta), no solamente X,CX,CCX. CP(theta)
es una fase controlada ideal, no una rotacion ya aproximada en Clifford+T.
Con m=5, la IQFT contiene 4 fases -pi/2, 3 fases -pi/4, 2 fases -pi/8 y
una fase -pi/16. El signo y las permutaciones se comprobaron contra la
matriz FFT normalizada para m=1..6, antes y despues de quitar los SWAP.

### Registro del circuito ideal completo, por ejecucion

p29_complete_resources.json, parametros p=29,m=5:

    X:    1
    CX:   11030
    CCX:  42160043
    H:    10
    CP:   10
    Total de instrucciones unitarias en esta base mixta: 42171094
    Mediciones: 5
    Qubits logicos: 231

La suma de instrucciones en esta base no representa tiempo de ejecucion:
una CP, una H y una CCX no tienen necesariamente el mismo coste fisico.
No se reportan T-count, profundidad, precision de sintesis de rotaciones,
conectividad, routing, correccion de errores ni qubits fisicos.

### Trabajo clasico real por medicion

classical_trace instrumenta recovered_orders mediante wrappers temporales
que delegan a las funciones reales y se restauran al terminar. No modifica
el archivo R5 ni sustituye el resultado con un mock ficticio. Se registran
los escalares comprobados, llamadas a classical_add y entradas a la
factorizacion real. Cada llamada a scalar_multiple(d) contiene exactamente
bit_length(d)+popcount(d) llamadas a classical_add, segun su bucle actual.
Algunas llamadas retornan por identidad u opuesto sin ejecutar formulas
de campo; el registro las distingue de duplicaciones y sumas ordinarias.

    y=0:  sin orden recuperado, 1 multiplicacion escalar, 2 llamadas de grupo
    y=13: orden 5, 6 multiplicaciones escalares, 24 llamadas de grupo;
          candidato factorizado 5
    y=3:  orden 5, 7 multiplicaciones escalares, 35 llamadas de grupo;
          candidato factorizado 10
    y=15: orden 5, 7 multiplicaciones escalares, 35 llamadas de grupo;
          candidato factorizado 15

Estas cifras corresponden a UNA llamada recovered_orders por medicion,
incluidos chequeos repetidos que realiza esa funcion. No incluyen la
llamada extra verified_candidates que el CLI original usa para imprimir
ni su validacion exhaustiva clasica del simulador. No representan una
media ponderada con la distribucion cuantica: el JSON registra los 32
casos individualmente. No se suman todos los casos como coste de un shot.

Una multiplicacion escalar clasica usa O(log d) llamadas de grupo. Si
C_group(w) denota el coste en bits de una operacion clasica de punto,
su coste se expresa O(log(d)*C_group(w)); no se sustituye C_group por 1
al afirmar un coste en bits. La expansion por fracciones continuas tiene
O(m) convergentes y opera con enteros de O(m) bits, no operaciones de
coste fisico constante. El registro de llamadas complementa, no sustituye,
el analisis de aritmetica clasica de enteros y campo.

### Limitacion de factorizacion y repeticiones

prime_factors_trial puede probar O(sqrt(d)) divisores de un candidato d.
Cada prueba implica operaciones de enteros; para d de O(w) bits esta
cantidad puede crecer exponencialmente con w. La referencia pequena NO
justifica una cota total polinomica del proceso certificado por el mero
hecho de que la parte cuantica tenga una cota polinomica. Sustituir esa
factorizacion, o reformular la recuperacion/certificacion, requiere decidir
el modelo y analizarlo explicitamente: no se cambia silenciosamente aqui.

Para R ejecuciones cuanticas independientes, deben separarse:

    Precomputacion clasica (una vez)
    + R veces el circuito cuantico
    + posprocesamiento de las mediciones efectivamente obtenidas

La probabilidad historica 0.6940239016 pertenece solo a esta instancia,
a su circuito ideal y al posprocesamiento definido. No es una garantia
uniforme para todas las curvas ni implica que todo shot tenga exito.
Un protocolo que acumule informacion entre shots tendria otro analisis.
El tiempo de simulacion que recorre 2**m entradas no forma parte del coste
de una ejecucion del algoritmo en una computadora cuantica.

### Validacion y pendientes de R6

Cuatro nuevas pruebas pasaron: matrices IQFT y eliminacion exacta de SWAP,
composicion de conteos, trazas reales para las 32 mediciones de F29 y
comprobacion de posprocesamiento en la curva pequena F5 de orden 3.
El JSON se genero a partir del registro real aritmetico del paso 4 y
contiene los conteos cuanticos y todas las trazas clasicas.

El inventario de una ejecucion ideal queda documentado, pero R6 no se
declara terminado como comparacion cientifica: falta alinear metricas y
alcance con las referencias, decidir el modelo escalable de recuperacion
y revisar las afirmaciones globales del manuscrito. No se ha modificado
el circuito R5, su snapshot de la memoria ni el paper.

Desde output/r6:

    python -s -B -m unittest test_complete_resources -v
    python -s -B complete_resources.py --output p29_complete_resources.json

## Reproducir

Desde output/r6:

    python -s -B -m unittest test_resource_model -v

En esta maquina se utilizo Python de Anaconda con Qiskit 2.0.0. El primer
intento encontro una mezcla incompatible de paquetes Qiskit en el directorio
de paquetes del usuario. La opcion -s excluye ese directorio de esta ejecucion
y selecciona la instalacion coherente de Anaconda; no instala, elimina ni
modifica paquetes. La opcion -B evita escribir caches de bytecode.

Las pruebas confrontan las formulas con len(circuit.data) en los circuitos
reales, comprobando tambien que todas las instrucciones son de la familia
permitida. Se incluyen modulo potencia de dos, constantes negativas y cero.
Estas pruebas validan el conteo, no repiten las pruebas funcionales de R5.
