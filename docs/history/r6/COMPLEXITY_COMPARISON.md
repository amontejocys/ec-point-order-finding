# R6: complejidad comparable, aparte de los conteos pequenos

No modifica el articulo. Complementa COMPLEXITY_DEFINITION.md: sus cotas
anteriores siguen siendo validas, pero la repeticion admite una cota
asintotica mas ajustada usando el analisis estandar.

## Parametros comunes

ell=ceil(log2(p)); m bits escalares; Q=2**m>B**2, B cota de Hasse.
La menor potencia suficiente implica m=O(ell). No sustituir ell por los
bits de r sin una hipotesis adicional que los haga comparables.
eps es el error permitido en recuperacion ideal, no error de hardware.

## Escalado del componente cuantico

| Arquitectura | Una suma controlada | Una evaluacion + IQFT | Qubits secuenciales |
| --- | --- | --- | --- |
| Referencia implementada, cadenas limpias MCX | O(ell**6) | O(m*ell**6+m**2) | O(m+ell**2) |
| Kernel optimizado publicado como referencia, no implementado aqui | O(ell**2*log(ell)) | O(m*ell**2*log(ell)+m**2) | O(m+ell) |

La segunda fila usa el escalado de suma controlada de Roetteler et al.,
seccion 5: https://arxiv.org/pdf/1706.06752 . Su formula numerica contiene
coeficientes ajustados, y su total ECDLP multiplica por 2n. Aqui solo se
usa el escalado del paso controlado, con ell como bits del campo. No se
identifica su algoritmo completo ECDLP con nuestro order finding, ni se
afirma compatibilidad inmediata de codificacion/casos especiales.
La memoria m+ell supone integrar ese kernel conservando un registro
escalar; no se copia un conteo de qubits ECDLP como conteo medido propio.

Con m=O(ell), las filas dan O(ell**7) y O(ell**3*log(ell)) por ejecucion.
Son comparaciones de cotas/modelos, no pruebas de inferioridad ajustada,
tiempos ni benchmarks del mismo circuito. Nuestra cota no es un Theta.
Las rotaciones CP siguen ideales; no incluye sintesis Clifford+T ni ruido.

## Presupuesto T: dos cotas compatibles

La demostracion finita ya disponible da exito por shot >=phi(r)/(16*r),
y el presupuesto numerico conservador T=ceil(16*nu_B*ln(1/eps)).
De ahi se habia obtenido T=O(ell*ln(1/eps)), valido pero holgado.

El resultado clasico phi(r)/r=Omega(1/log(log(r))) para r grande, utilizado
por Shor en su seccion 5, mejora el limite asintotico. Como r<=B y
log(log(B))=O(log(ell)), ajustando la constante para los ordenes pequenos:

    Exito por shot >= c / (1+log(ell)), para una constante c>0.
    T = O((1+log(ell))*ln(1/eps)) es suficiente.

Fuente: https://arxiv.org/pdf/quant-ph/9508027 , seccion 5. La constante
asintotica no se convierte en un presupuesto numerico de 32 shots. Los
443 del ejemplo p29 siguen siendo una cota finita explicita valida, no
un requisito minimo. La garantia es probabilistica, no certificacion.

## Resultado con el mismo objetivo de exito

Para la implementacion de referencia seleccionada:

    G_quantum = O(ell**7*(1+log(ell))*ln(1/eps)).
    C_classical_online = O(ell**4
                          + ell**5*(1+log(ell))*ln(1/eps)
                          + A*ell**4),

donde A cuenta tentativas convencionales de firma. No se da protagonismo
a A: el coste de firma puede reportarse por tentativa. C_key, si falta,
es O(ell**4) en estas cotas holgadas; hashing esta excluido cuando z es
entrada. Compilacion/sintesis offline y otras validaciones de parametros
no estan incluidas en C_classical_online. Ver nota del cotejo del ZIP.

Para eps constante y por tentativa de firma, puede resumirse:

    Cuantico: O~(ell**7).
    Clasico online: O~(ell**5).
    Qubits: O(ell**2).

O~ oculta factores polilogaritmicos del tamano, no una potencia extra de
ell. La anterior O(ell**8*ln(1/eps)) es una cota mas debil, no una medida
del circuito ni una contradiccion con este refinamiento.

Si se integrase el kernel optimizado publicado bajo condiciones adecuadas,
el componente cuantico tendria O(ell**3*(1+log(ell))**2*ln(1/eps)), o
O~(ell**3) para eps constante. Eso NO es coste del codigo actual. Tampoco
autoriza llamar O~(ell**3) al proceso hibrido completo con nuestro
posprocesamiento, cuyo limite clasico se reporta separadamente.

## Comparacion clasica y conclusiones permitidas

La enumeracion usa O(r*C_group(ell)) trabajo clasico, frente a las cotas
polinomicas anteriores en ell. Para hablar de separacion exponencial con
el tamano del campo hace falta un regimen como r=2**Theta(ell). No vale
para todo punto, por ejemplo los de orden pequeno. Esa comparacion es
contra enumeracion, NO contra el mejor algoritmo clasico de orden.
R7 debe incluir metodos genericos y point counting mas factorizacion,
sin mezclar operaciones de grupo, operaciones en bits y compuertas como
si fueran tiempos fisicos comparables.

Lo establecido por R6 es una cota polinomica propia coherente con el
codigo y una comparacion honesta con aritmetica optimizada publicada.
No se acredita mejora asintotica sobre esa aritmetica ni novedad por
componente; el posicionamiento del aporte integrado debe tratarse aparte.
