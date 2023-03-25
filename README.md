# Practica2 
En esta práctica he subido varios archivos distintos. Explicaré un poco sobre qué va cada uno. 

-El archivo 'practica2': Es la solución básica al problema planteado, en el que se consigue que el puente sea seguro, es decir, que en el puente solo haya coches en 
dirección o peatones, y también que pasen todos los peatones y coches sin que haya deadblocks. No se tiene en cuenta en esta opción que pueda haber inanición, es decir, 
que alguna de las variables nunca llegue a entrar en el proceso. 

-El archivo 'practica2_inanicion': Es la primera 'solución' al problema de inanicion de una manera un poco sencilla que luego se va desarrollando. En este archivo lo 
que se hace es contabilizar los coches en cola. Cuando llega a un número predeterminado de coches esperando, los peatones deben parar de pasar y darles paso. Así se 
evita que si hay una gran cantidad de peatones pasando pues que se forme una larga cola de coches querien pasar por el puente. 

-El archivo 'practica2_inanicion2: Aquí se procede a elaborar una solución bastante parecida a la nombrada en el archivo anterior. Lo que pasa es que en este caso lo 
que se contabiliza es el número de peatones esperando. Cuando se alcanza el número predeterminado los coches deben dejarlos pasar. 

-El archivo 'practica2_inanicion3: Un poco la idea de este programa es juntar las dos ideas anteriores. Se contabiliza el número de coches y peatones esperando para que
cuando se pasen del límite impuesto, los otros les dejen pasar. En este caso hay que tener en cuenta que ambos puedes cumplir las condiciones de que haya muchos coches 
y peatones esperando, lo que puede llevar a un bloqueo del proceso. Por ello, se impone una condición extra a los peatones de que dejen pasar a los coches en caso de que 
ambos haya muchos en espera. 

-El archivo 'practica2_inanicion4: Se podría decir que esta es la mejor solución y más completa. A parte de lo comentado en el archivo anterior, en este también se hace 
distinción entre los coches del sur y del norte. La idea es básicamente la misma que para la distinción entre peatones y coches nombrada anteriormente. Se impone un
límite para cada dirección y cuando en una de ellas hay muchos coches esperando, los otros les tienen que dar paso. En este caso también hay que tener en cuenta que como 
tenemos peatones, pueden acumularse muchos coches en ambas direcciones y que se produzca un bloqueo. Para evitarlo, se le impone una condición extra a los coches que vienen 
por el norte, los cuales deben dejar pasar a los del sur si ambos tienen una gran cantidad de coches esperando. Todo esto junto a lo del archivo anterior hace que en esta 
opción se tenga en cuenta todas las posibles opciones (que hayan muchos coches o peatones esperando y que dentro de los coches hayan muchos en el sur o el norte). 
