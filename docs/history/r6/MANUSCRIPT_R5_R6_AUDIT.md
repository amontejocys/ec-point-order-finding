# Cotejo de R5/R6 con el ZIP actualizado

Archivo inspeccionado en modo lectura:
Shor_s_Algorithm_Adapted_for_Determining_the_Order_of_Elliptic_Curves__1_ (3).zip.
SHA256 antes y despues: 9563dda64b1895d62033c45aead36cb5bb040b94e796e836f08dc00fc1b4fb99.
Ningun archivo del articulo fue extraido para editarlo ni modificado.
Esta nota es una auditoria tecnica, no una propuesta de redaccion.

## Estructura y revisiones ya presentes

main.tex usa REVTeX 4.2, incluye ocho archivos sec/ y main.bib.
main.tex:42-43 ya carga xcolor y define revision como grupo de color azul.
El abstract completo esta en revision. Methods contiene dos subsecciones
azules: representacion de puntos (15-30) y evaluacion reversible (49-96).
Por tanto, R5 tiene integracion PARCIAL previa; no partir de cero ni borrar
esa parte por suponer que no se hizo ningun cambio.
El cofactor h=6 esta corregido en appendix:52-53. El resto del ejemplo
todavia usa Q16, tabla, periodo4 y toggle.
ProosZalka2003, Roetteler2017, Haner2020 y Litinski2023 existen en main.bib.
No se detectaron claves citadas ausentes. No se encontro una entrada de
Cheung-Mosca; su posicionamiento bibliografico sigue siendo R8.

## Lugares que deben reconciliarse ANTES de redactar

| Archivo y lineas originales | Inconsistencia | Decision tecnica necesaria |
| --- | --- | --- |
| methods:39-46 | Exito constante de CF sin condiciones; QFT frente a IQFT local | Usar recuperacion probabilistica y condiciones de resolucion |
| methods:84-96 | Nuevo U inicializa en enc(O), no salida binaria cero arbitraria | Mantener contrato de traslacion; apendice no puede conservar automaticamente XOR tabular |
| results:4-8,21-23 | Algoritmo modificado, idx y parity | Nuevo metodo conserva Shor estandar y codificacion de coordenadas |
| results:29-43 | Tabla, toggle, una sola medicion y sin fallo/reintento | Pipeline aritmetico, presupuesto T, retorno sin candidato/no minimalidad; firma condicionada al orden correcto |
| results:48,62-75 | n bits de r sustituye ell; C es evaluacion completa pero se multiplica por m | C_add por suma controlada, m separado de ell; aritmetica se paga por bits de p |
| results:79-87 | Teorema hereda coste de otros circuitos, lookup doblemente contado | Separar costes propios de referencias y modelo de una evaluacion de f |
| results:93-97 | Supuestos externos y parity ya no describen el codigo | Actualizar alcance de la implementacion real |
| results:101-122 | Tabla en unidades arbitrarias no comparables y errores numericos | Separar tabla de recursos medidos de cotas y baselines; formulas exactas declaradas |
| results:126-138 | Equivalencia de firmas universal y recuperacion constante | Condicionar a orden exacto y parametros adecuados; distinguir modelo ideal de compuertas reales |
| results:142-150 | Limitaciones y conclusiones siguen con lookup/parity | Reconciliar tras terminar comprobaciones |
| appendix:3-27 | Sintesis por tabla y codificacion idx | Sustituir especificacion por aritmetica y contratos reales |
| appendix:32-47 | Factores, inversion, m*C_full, exito 4/pi^2 y amplificacion constante | Usar costes de bits coherentes y presupuesto de repeticiones sustentado |
| appendix:52-55 | Nuevo cofactor, pero resultado numerico antiguo | Conservar datos geometricos; reemplazar experimento inconsistente por resultados verificables |
| data_availability:3 | Repo externo y statevector descritos como implementacion actual | Aun no se subieron estos archivos; no afirmar que ese repo reproduce el nuevo experimento |

Las lineas son internas al ZIP; el JSON registra ubicaciones de marcadores.

## Tabla I: diagnostico numerico

manuscript_zip_audit.csv evalua exactamente las formas 2**n,
n**3*log2(n) y 2**(2*n)*n**2 solo como diagnostico de las cifras antiguas.
Las dos primeras columnas coinciden aproximadamente con esos modelos
redondeados, pero eso NO vuelve comparables sus unidades ni costes.
La tercera coincide para n=8,16,32 y falla de forma apreciable para
n=64,128,256. El cociente publicado/expresion es 0.531,0.633,3.869.

No hay una unica correccion por un factor omitido. No recuperar una tabla
de tiempos sustituyendo numeros arbitrarios. El CSV de los cinco circuitos
reales ya generado usa una base declarada y conteos cotejados.
La tabla de baselines clasicos requiere cerrar R7; no se inventa SEA aqui.

La sintesis historica tabular del apendice evalua f completa UNA vez:
si cada fila cuesta O(m*n_out), G_lookup=O(Q*m*n_out). Multiplicar otra
vez por m al insertarla como C_full en el modelo de sumas controladas es
doble conteo. Al retirar lookup, esta cifra deja de ser coste del metodo
actual; si se conserva como antecedente, debe conservarse su modelo correcto.

## Calculo adicional: firma y verificacion clasicas

El Algoritmo 1 recibe z ya calculado: hashing no forma parte de esa entrada.
Definir b_r=ceil(log2(r)), que no es el entero n usado para el orden en la
descripcion ECDSA. Como r<=B, b_r=O(ell), pero no necesariamente b_r=ell.

Una tentativa de firma usa:

    C_sign = O(b_r*C_group(ell) + C_inv(b_r) + C_mul(b_r)
               + C_reduce(ell,b_r)).

El primer termino es kP clasico (no sustituido por order finding); el
segundo es k^{-1} mod r; los demas pagan z+r_sigma*d, reducciones y s.
Para aritmetica escolar con las cotas holgadas ya adoptadas, C_group(ell)
y C_inv(b_r) tienen cotas cubicas, multiplicacion es cuadratica y la
reduccion de coordenada tambien es polinomica. Para z de O(b_r) bits,
C_sign=O(ell**4). Si z es mas largo, incluir su reduccion o la conversion
estandar del hash; no ocultar esa dependencia en un hash arbitrario.

La clave publica dP se calcula una vez por clave: O(b_r*C_group(ell)).
La verificacion usa dos multiplicaciones escalares y una suma, inversion
mod r y operaciones de enteros: la misma cota conservadora O(ell**4).
No se incluye verificacion si el protocolo solo firma, pero el experimento
si la ejecuta para comprobar equivalencia funcional.

Para A tentativas de nonce, y un flujo que recalcula el orden cada vez:

    Coste cuantico = T*G_Q.
    Coste clasico online = C_pre_constants + T*C_post + A*C_sign
                          + C_key (si no estaba preparada).

Si L mensajes usan la MISMA curva y punto, el orden puede recuperarse
UNA vez y reutilizarse. No atribuir T circuitos necesarios a cada firma:

    Coste cuantico de setup = T*G_Q.
    Coste clasico = C_pre_constants + T*C_post + C_key
                   + sum_(i=1..L) A_i*C_sign_i.

La construccion/sintesis clasica offline sigue separada. Si se pretende
tiempo total desde fuente hasta firma, hay que incluirla y medirla/modelarla;
las cotas anteriores no son tiempos de compilacion.

No existe aqui una garantia universal de un numero constante de reintentos
para curvas arbitrarias pequenas. Se puede limitar A y permitir fallo,
o declarar una hipotesis de probabilidad de nonce valido. No ampliar la
garantia de recuperacion del orden a una garantia de firmar sin condiciones.

## Nueva validacion de integracion

signature_integration.py utiliza el orden recuperado de mediciones reales
del experimento p29,Q2048. El evaluador conoce el orden de referencia; el
recuperador no. Para T=4, las 100 repeticiones recuperaron 5 y produjeron
la firma de prueba (1,4), con d=2, nonce=1 y z=2, verificada correctamente.
Estos z y nonce son NUEVOS datos de ensayo, no datos reconstruidos del
experimento historico: el ZIP no los especifica.

Ademas, se comprobaron todas las 80 combinaciones d=1..4,k=1..4,z=0..4:
64 firmas validas iguales a la referencia independiente y 16 tentativas
con s=0 que deben reintentarse. Tres nuevas pruebas pasaron.
Una prueba muestra que usar el multiplo 10 en lugar de 5 cambia la firma
y no satisface la verificacion de referencia del subgrupo de orden 5.

Fuente de las ecuaciones de firma/verificacion y rechazo de componentes
cero: SEC 1 v2, 4.1.3 y 4.1.4, https://www.secg.org/sec1-v2.pdf .
El codigo es aritmetica de prueba con nonce explicito y entero z, NO una
implementacion segura, certificacion de parametros ni conformidad completa
SEC1. No demuestra seguridad, hashing o interoperabilidad con bibliotecas
ECDSA estandar en dominios arbitrarios/compositos. ECDSA exige dominios
adecuados de orden primo; el estudio de order finding puede incluir ordenes
compuestos sin afirmar que todos esos puntos sirven para ECDSA.

## Estado al terminar este cotejo

Disponibles: circuitos y contratos R5, validaciones reales, recuperacion
probabilistica, ensayos ideales, recursos regenerados, limites de coste y
repeticiones, costes de firma y evidencia funcional de integracion toy.
El ZIP permanece sin modificaciones y se conserva el snapshot de memoria.

Antes de redactar quedan decisiones de alcance, no numeros por inventar:
seleccionar la tabla que se presentara, explicitar si el orden se recupera
en setup o por invocacion, fijar el tratamiento de fallos/reintentos y no
mezclar el comparador clasico pendiente de R7 con los conteos propios R6.
No afirmar que R5/R6 quedaron integradas ni que toda observacion del
revisor esta atendida antes de revisar esos cambios con el usuario.

## Alcance fijado tras el cotejo

El usuario pide no dar protagonismo a los reintentos. Se distingue:

- T es el presupuesto de ejecuciones cuanticas para recuperar el orden.
  Sigue explicitamente en las formulas; no se elimina ni se llama a todos
  esos shots una sola ejecucion cuantica.
- Los rechazos convencionales de firma (componentes cero o nonce no valido)
  se mencionan brevemente. No son una contribucion, seccion experimental
  ni nuevo parametro central. C_sign se reporta POR TENTATIVA; no se
  convierte sin hipotesis adicionales en coste esperado de firma exitosa.
- El coste basico de la integracion es C_pre_constants + T*C_post + C_sign,
  mas C_key si la clave publica no estaba disponible. El conteo cuantico
  sigue siendo T*G_Q, en otra unidad. La equivalencia funcional se condiciona
  al orden exacto y a parametros adecuados de firma.

Recomendacion de presentacion para validar con el usuario: recuperar el
orden durante la preparacion de una instancia (E,P) y reutilizarlo mientras
no cambien curva/punto; el caso de una sola firma queda incluido. No usar
esto como validacion de seguridad de parametros ni como certificacion de
minimalidad. No hace falta repetir order finding por mensaje.

Recomendacion de tabla R6: conteos reales por UNA ejecucion de los cinco
circuitos validados, separados de probabilidades y trabajo clasico. Aplicar
T mediante la formula general. La comparacion de baselines de R7 queda
en una tabla o analisis distinto: no conservar unidades arbitrarias como
si fueran tiempos comparables. El articulo aun no se ha modificado.
