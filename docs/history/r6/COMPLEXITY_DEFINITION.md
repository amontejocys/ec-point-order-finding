# R6: definicion matematica del coste y alcance

Esta nota fija las cotas del componente de order finding y su recuperacion
probabilistica. No edita el paper, sus tablas ni la memoria de Overleaf.
No incluye automaticamente otros pasos del protocolo de firmas.

## Hipotesis y parametros

p primo > 3, curva no singular y P finito valido (orden r >= 2).
ell = ceil(log2(p)), B = p+1+isqrt(4*p), r <= B.
Q = 2**m > B**2; elegir la menor potencia asi implica m = O(ell).
Codificacion inyectiva de los puntos, aritmetica exacta, auxiliares limpios,
IQFT ideal y ejecuciones independientes sin ruido.

No se supone r conocido ni par. eps en (0,1) es el error de recuperacion
permitido; no es precision de sintesis de rotaciones.

## Costes de una ejecucion y convenciones

C_add(ell,P_j) es una actualizacion controlada completa, incluidos casos
especiales y uncomputation, con P_j = 2**j P precomputado clasico.

    G_scalar = sum_(j=0..m-1) C_add(ell,P_j).

P_j=O puede omitirse sin afectar el limite de m bloques. Nunca se cuenta
m veces una evaluacion completa de kP. En el inventario ideal mixto:

    G_Q = G_scalar + 1 + 2*m + m*(m-1)/2 + 3*floor(m/2).

El 1 prepara O; hay m H iniciales y m H en IQFT; las fases CP se cuentan
como instrucciones ideales. Medir m qubits se registra aparte.

En la referencia compacta implementada:

- MCX como instruccion: C_add = O(ell**5).
- MCX sintetizada mediante la cadena limpia de CCX auditada:
  C_add = O(ell**6), G_Q = O(m*ell**6 + m**2).
- Qubits logicos secuenciales: O(m+ell**2), incluidos auxiliares de MCX.

Son limites superiores conservadores derivados de los bucles del codigo,
no cotas ajustadas ni estimaciones de los circuitos optimizados publicados.
La base completa incluye X,CX,CCX,H,CP(theta). No es Clifford+T ni una
estimacion de profundidad, conectividad, correccion de errores o tiempo.
Para m=O(ell): una ejecucion usa O(ell**7) instrucciones en esta base.

## Trabajo clasico

Las potencias principales requieren m-1 duplicaciones; otras constantes
auxiliares por bloque mantienen O(m) operaciones de punto.
C_pre_constants = O(m*C_group(ell)), para curva/punto ya validados.
La construccion y sintesis clasica del circuito, C_build, es una tarea
offline adicional: no se equipara a esta precomputacion de constantes ni
se ha medido su coste en bits o tiempo. Las cotas siguientes describen
ejecucion y posprocesamiento, no el tiempo completo de compilar un programa.

Por medicion hay O(m) convergentes; d<=B tiene O(ell) bits y verificar dP=O
requiere O(ell) operaciones de punto. Actualizar gcd usa enteros de O(ell)
bits, porque el acumulador divide a candidatos <=B.

    C_post = O(C_CF(m) + m*ell*C_group(ell) + m*C_gcd(ell)).
    C_classical_online = C_pre_constants + T*C_post.
    C_classical_with_build = C_build + C_classical_online.

Con aritmetica escolar y cotas deliberadamente holgadas, pueden usarse
C_CF(m)=O(m**3), C_group(ell)=O(ell**3), C_gcd(ell)=O(ell**3).
La primera cuenta O(m) pasos con operaciones de enteros de O(m) bits;
las otras permiten Euclides extendido con O(ell) pasos y operaciones
escolares de O(ell**2). No son las mejores cotas conocidas.
Resulta C_post=O(m**3+m*ell**4), y con m=O(ell), O(ell**5).
No hay division de prueba ni factorizacion en el recuperador.

## Cota finita suficiente de exito: demostracion conservadora

Esta es una derivacion elemental para la distribucion ideal, no una
mejora de Shor ni una implementacion de Ekera. Shor, seccion 5, fundamenta
la recuperacion por convergentes y el papel de phi(r)/r:
https://arxiv.org/abs/quant-ph/9508027 . La constante 1/16 que sigue es
una cota propia deliberadamente mas debil; no se atribuye a esa fuente.

Para cada s coprimo con r, elegir y_s entero mas cercano a Q*s/r da:

    |y_s/Q - s/r| <= 1/(2Q) < 1/(2*r**2).

Por el criterio clasico de convergentes, el denominador r aparece.
Se verifica rP=O; cualquier otro candidato aceptado es multiplo de r,
por lo que el gcd de todos ellos tambien es r. Los y_s son distintos.

Para acotar la probabilidad de y_s, separar las r clases de k por k mod r.
Cada clase tiene N entradas, N <= Q/r+1. Su amplitud, salvo una fase
global, es una suma geometrica S_N de paso theta, donde |theta|<=pi*r/Q.
Como Q>r**2 y r>=2, Q>=2r y:

    N*|theta|/2 <= 3*pi/4.
    |S_N| = N*|sinc(N*theta/2)| / |sinc(theta/2)| >= N/4.

Aqui sinc(u)=sin(u)/u. En [0,3*pi/4] es al menos
sin(3*pi/4)/(3*pi/4)=2*sqrt(2)/(3*pi)>1/4, y el denominador es <=1.
El limite en theta=0 tambien satisface la desigualdad. Al trazar las
salidas ortogonales, Pr(y_s)=sum_classes |S_N|**2 / Q**2.
Por Cauchy-Schwarz, sum N**2 >= Q**2/r. Entonces:

    Pr(y_s) >= 1/(16*r).
    Pr(aceptar r en un shot) >= phi(r)/(16*r).

Si q_1<...<q_w son los primos distintos de r, q_i>=i+1 y:

    phi(r)/r = product(1-1/q_i) >= product(i/(i+1)) = 1/(w+1).
    w <= floor(log2(r)) <= floor(log2(B)).

Definir nu_B=1+floor(log2(B)) da alpha_0=1/(16*nu_B), conocido sin r.
nu_B no es el cofactor h de la curva; no se reutiliza esa notacion.
Con T shots independientes, fallar en alcanzar el orden tiene probabilidad:

    Pr(fallo) <= (1-alpha_0)**T <= exp(-alpha_0*T).
    T >= ceil(16*nu_B*ln(1/eps)) es suficiente.

Llegar a r mediante gcd de varios multiplos puede mejorar el exito;
esta cota solo usa el evento suficiente de aceptar r directamente.
Garantiza recuperacion exacta con probabilidad >=1-eps bajo las hipotesis,
NO un certificado determinista de minimalidad del resultado observado.
Incluye como fallo tanto no obtener candidato como devolver un multiplo.

## Complejidad con error fijado

Como nu_B=O(ell), esta eleccion conservadora da T=O(ell*ln(1/eps)).
Para la referencia, en la base ideal mixta especificada:

    Total cuantico: O(ell**8 * ln(1/eps)).
    Clasico online: O(ell**4 + ell**6 * ln(1/eps)).
    Qubits logicos secuenciales: O(ell**2).

Con eps constante se reducen a O(ell**8), O(ell**6), O(ell**2).
No se suman costes clasicos en bits y compuertas cuanticas como una misma
unidad. No se afirma ventaja sobre el mejor metodo clasico (R7), ni una
nueva complejidad de Shor. Una cota mas ajustada de repeticiones es posible
con analisis estandar mas fuertes; no se necesita para justificar esta cota.

## Experimentos frente a garantia

Para p=29, B=40, nu_B=6, eps=0.01: Q=2048 y T=443 es un presupuesto
suficiente CONSERVADOR. No es el minimo ni una estimacion del numero
necesario en promedio; no se ha ejecutado ese circuito y presupuesto aqui.
El piloto observa exito con presupuestos menores, pero no reemplaza la
garantia. El experimento historico Q=32 no cumple Q>B**2 y queda fuera
del alcance de este limite uniforme, aunque r=5 permita buen rendimiento.

## Estado de R6

La definicion matematica queda especificada y sustentada por derivaciones,
conteos y pruebas auxiliares. Integracion editorial pendiente: reemplazar
definicion de C, ecuacion global, tabla y afirmaciones incompatibles en el
manuscrito, revisar factores logaritmicos y separar referencias optimizadas.
NO se declara R6 completamente atendido antes de revisar esos lugares.
No se modifica automaticamente ningun archivo del paper.
