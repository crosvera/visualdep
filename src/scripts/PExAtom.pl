#!/usr/bin/perl
####################
#name: PExAtom.pl
#desc: setea en uel acampo del b-factor(61-66) de formato PDB el valor del PE de cada Atomo 
#input: Archivos entrada uno(.phi) proveniente de multivalue con las coordenadas por Atomo y sus PE y el otro un PDB original(campos ATOm importante).
#output: archivo PDB.
#Autor: njana@udec.cl Natalia Jaña P. 
#Carpeta de ejecucion /home/nati/VisualDep/APBS/script/
####################

$pdb=$ARGV[0];#nombre de proteina en formato pdb
$phi=$ARGV[1];#PE por coordenada de atomo
$diff=$ARGV[2];#nombre archivo de salida .pdb

open(PDB,$pdb);#archivo PDB
open(PHI,$phi );   # resultadp de multivalue
open(DIFF,">$diff"); # guardar PDB con b-factor reemplazado por PE por atomo. 

      while($pdb=<PDB> ){       # lee archivos línea a línea de PDB
            if ($pdb=~/^ATOM/)      {#lee tb de PHI..
              $phi=<PHI>; #si encunetra un ATOm lee inmediatamente en el archivo multivalue
              @phi4=split(",",$phi);#separa cons plit la linea posee 4 elementos
              $num=$phi4[3];# el ultimo elemento nos interesa
              $num=sprintf("%6.1f",$num);#formateo  %6.2f= 6 columnas(espacios) puede ocupar y como maximo 2 decimales
              substr($pdb, 60, 6, $num);           #reemplazo el $num en la posicion 60 del pdb original.          
#55 - 60      Real(6.2)        occupancy  Occupancy.
#61 - 66      Real(6.2)        tempFactor Temperature factor.
            # substr($pdb, 56,6, $num); 
	 
     print DIFF $pdb;#graba en archivo nuevo.linea por linea 
 	}
      }   

close PDB;
close PHI;
close DIFF;

