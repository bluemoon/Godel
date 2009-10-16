#include <stdio.h>
#include <stdlib.h>
#include <libguile.h>

int main (int argc, char *argv[])
{
	SCM func_symbol;
	SCM func;
	
	scm_init_guile();
	
	// Load the scheme function definitions
	scm_c_primitive_load ("script.scm");	
	
	func_symbol = scm_c_lookup("do-hello");
	func = scm_variable_ref(func_symbol);
	
	scm_call_0 (func);

	exit(EXIT_SUCCESS);
} 

