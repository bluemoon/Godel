#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "Python.h"
#include "scheme.h"
#include "scheme_ext.h"

static PyObject *SchemeError;

static void scheme_dealloc(scheme *self){
  self->ob_type->tp_free((PyObject*)self);
}

static PyObject *scheme_new(PyTypeObject *type, PyObject *args, PyObject *kwds){
  scheme *self = NULL;
  self = (scheme *)type->tp_alloc(type, 0);
  if (self != NULL){

  }

  return (PyObject *)self;

}

PyObject *scheme_init(scheme *self, PyObject *args, PyObject *kwds){
  // For the enviroment setup
  self->env = scheme_basic_env();
  scheme_default_handler();

  scheme_add_global("py", scheme_make_prim(scheme_callback), self->env);
  self->callbacks = PyDict_New();
  
  return 0;
}


static PyObject *scheme_set_callback(scheme *self, PyObject *args){
  PyObject *temp;
  PyObject *function_name;
  Scheme_Object *callback;
  Scheme_Object *Py_type;
  Scheme_Object *var;

  callback = scheme_alloc_object();
  var = scheme_alloc_object();

  if (PyArg_ParseTuple(args, "OO", &function_name ,&temp)) {
    if (!PyCallable_Check(temp)){
      PyErr_SetString(PyExc_TypeError, "parameter must be callable");
      return NULL;
    }
    Py_XINCREF(temp);

    char *pre = "callable_";
    char *pyString = PyString_AsString(function_name);
    char *func_string = (char *)calloc(strlen(pre) + strlen(pyString) + 1, 
                        sizeof(char));

    strcat(func_string, pre);
    strcat(func_string, pyString);

    
    Py_type = scheme_make_type("<PyObject>");
    //callable = scheme_make_type("<callable>");
    SCHEME_TYPE(callback) = Py_type;
    SCHEME_PTR_VAL(callback) = temp;
 
    SCHEME_TYPE(var) = Py_type;
    SCHEME_STR_VAL(var) = func_string;

    scheme_add_global(pyString, temp, self->env);

    PyDict_SetItem(self->callbacks, function_name, temp);
  }
  //
  Py_INCREF(Py_None); 
  return Py_None;
}

static Scheme_Object *scheme_callback(int argc, Scheme_Object *argv[]){
  printf("%d\n", argc);
  scheme_debug_print(argv[0]);
  //PyObject *result = PyEval_CallObject(py_compare_func, arglist);


  return scheme_true;
}

static PyObject *scheme_run_file(scheme *self, PyObject *args){
  PyObject *output;
  PyObject *tmp;
  output = PyList_New(0);
 
  FILE *scheme_file;
  const char *file;

  Scheme_Object *in_port;
  Scheme_Object *obj; 

  if(!PyArg_ParseTuple(args, "s", &file))
    return NULL;
  

  scheme_file = fopen(file, "r");
  if(scheme_file != NULL){
    in_port = scheme_make_file_input_port(scheme_file);

    while ((obj = scheme_read(in_port)) != scheme_eof){
      obj = SCHEME_CATCH_ERROR(scheme_eval(obj, self->env), 0);
      tmp = PyString_FromString(scheme_write_to_string(obj));
      PyList_Append(output, tmp);
    }

    fclose(scheme_file);
    return output;

  } else {
    return NULL;
  }


  //return result;
}


PyMODINIT_FUNC initscheme(void){
    PyObject *m;

    m = Py_InitModule("scheme", SchemeMethods);
    if (m == NULL)
        return;

    SchemeError = PyErr_NewException("scheme.error", NULL, NULL);
    Py_INCREF(SchemeError);
    PyModule_AddObject(m, "error", SchemeError);
    
    scheme_Type.tp_new = PyType_GenericNew;
    if (PyType_Ready(&scheme_Type) < 0)
        return;

    Py_INCREF(&scheme_Type);
    PyModule_AddObject(m, "scheme", (PyObject *)&scheme_Type);
    
    
}
