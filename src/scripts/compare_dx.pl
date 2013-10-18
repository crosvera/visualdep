#!/usr/bin/perl


$file_uno=$ARGV[0];#archivo uno para comparar
$file_dos=$ARGV[1];#archivo dos para comparar
$file_salida=$ARGV[2];#nombre archivo salida

open(ALL,"$file_uno");   # 
open(ALL2,"$file_dos"); # 
open(MIX,">$file_salida"); # crea archivo con diferencia cal>2bv8_resta
#leer la linea 12 encabezado de los resultados
	for($j=0;$j<11;$j++){
	  $all=<ALL>;
    	  $all2=<ALL2>;
	  print MIX $all;
	  print MIXDESV $all;
      }
      # lee archivos línea a línea
      #creamos contador para el arreglo final de la resta...
      $i=0;
      #inicializamos variable q cuenta el numero de datos y la q almacena la suma de los datos
      $sumData=0;
      # se tiene la ultima linea del encabezado la que cotiene la cantidad total de datos, de la grilla
      print "Comenzando resta de potenciales electrostaticos\n";
      if($all=~/\S+\s\S\s\S+\s\S+\s\S+\s\S+\s\S+\s\S\s\S+\s(\S+)\s\S+\s\S+/){
	  $countData=$1;	    
      }#end if      
	#se comienza a leer la data de la grilla  linea por linea
	while($all=<ALL> ){       # lee archivos línea a línea
	#$all=<ALL>;
        	$all_2=<ALL2>;
	# si la linea comienza con "attribute" copiar linea completa en 
	if ($all=~/^attribute/)	{
		print MIX $all; 
		while ($all=<ALL>){
			#	print MIX $all;
		}
	}
	else{	#guarda las coordenadas de la linea del archivo ALL
		if($all=~/(\S+)\s(\S+)\s(\S+)/){
			@all[0]=$1;@all[1]=$2;@all[2]=$3;
		}
		#guarda las coordenadas de la linea del archivo ALL_2
		if($all_2=~/(\S+)\s(\S+)\s(\S+)/){
			@all_2[0]=$1;@all_2[1]=$2;@all_2[2]=$3;
		}
		#realiza la resta (sub) 
		@sub[$i]=abs(@all[0]-@all_2[0]);
		@sub[$i+1]=abs(@all[1]-@all_2[1]);
		@sub[$i+2]=abs(@all[2]-@all_2[2]);
		
#contar los datos y sumarlos
		#$sumData=$sumData + @sub[$i]+@sub[$i+1]+@sub[$i+2];
		#se graba los resultados de la resta en el archivo all_MIX
		#valor referencial de corte Umbral obtenido por Kmeans
		#umbral=73.2328.. si es menor o igual queda como cero
		#$umbral=239.3351;
		#if (@sub[$i]<=$umbral){
			#	@sub[$i]=0;	
			#}
			#if(@sub[$i+1]<=$umbral){
				#@sub[$i+1]=0;
				#}
				#if(@sub[$i+2]<=$umbral){
					#@sub[$i+2]=0;
					#}
											       
		#print MIX "@sub[$i] @sub[$i+1] @sub[$i+2]\n" ;
  	        printf(MIX "%.6f",abs(@sub[$i]));
	        print MIX "e+00 ";
	        printf(MIX "%.6f",abs(@sub[$i+1]));
		print MIX "e+00 ";
		printf(MIX "%.6f",abs(@sub[$i+2]));
		print MIX "e+00\n";
												    
		#incrementar i
		$i=$i+3;
 		 }#end else
		 #$i=$i+3;#incrementar contador del arreglo con los valores restados..
	 }#end while 
	 #calcular promedio
	 $promedio=$sumData/$countData;
	#calcular desviacion estandar
	$varianza=0;
        $contadorPruebaArreglo=0;
	foreach $valor (@sub){
                $varianza=($varianza+($valor- $promedio)**2)/($countData-1);
		#	$contadorPruebaArreglo++;
        }
	$desvStand=sqrt($varianza);
	#print "$varianza\n";
	print "Listo desviacion estandar:  $desvStand\n";
	#print $contadorPruebaArreglo;
	
	#ahora escribir en archivo MIXcon desv,, rango mas apmlio de Ceros...

#end while
  close(ALL);             
  close(ALL2);           
  close(MIX);   
