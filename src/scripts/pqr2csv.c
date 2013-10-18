/******************************************************************************/
/*Program: pqr2csv                                                            */
/*Author: Ting Wang                                                           */
/*Email: twang@ucdavis.edu                                                    */
/*Institution: University of California at Davis                              */
/*Date: Dec 17, 2007                                                          */
/*Purpose: extract coordinates in csv format: x,y,z                           */
/*PDB format: ATOM=column 1-4;  N(C,O,..)=column14;  XYZ=column 31-54         */
/* only lines starting with ATOM are considered                               */
/*COMPILATION: cc -o pqr2csv pqr2csv.c                                        */
/*USAGE: >pqr2csv protein.pqr protein.csv                                     */
/******************************************************************************/
/* Modified by crosvera
 * return 1 in case of error, return 0 otherwise.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>


int main (
	int argc,         /* Number of args */
	char ** argv)     /* Arg list       */
{
	FILE  *fin,*fout;
	float X,Y,Z;
    char line[100];
	
    if((fin = fopen(argv[1] , "r")) == NULL)
	{
        printf("PQR file can not be opened .\n");
        exit(1);
    }
    if((fout = fopen(argv[2] , "w")) == NULL)
	{
        printf("CSV file can not be written .\n");
        exit(1);
    }

	while(fgets(line,100,fin))
	{
	    if(strncmp(line,"ATOM",4)==0||strncmp(line,"HETATM",6)==0){
	      
	        if(sscanf(line+30,"%f%f%f",&X,&Y,&Z)!=3)
	        {
                printf("XYZ is not complete");
                exit(1);
            }
	        fprintf(fout,"%f,%f,%f\n",X,Y,Z); /*no any space */
	    }
   	}/* end of while fgets() */
	
    fclose(fin);
    fclose(fout);

 return 0;
}

