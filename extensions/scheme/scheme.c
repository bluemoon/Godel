#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "Python.h"
#include "scheme_ext.h"


static PyObject *SchemeError;

static void VM_dealloc(VM *self){
  self->ob_type->tp_free((PyObject*)self);
}

static PyObject *VM_new(PyTypeObject *type, PyObject *args, PyObject *kwds){
  VM *self = NULL;
  self = (VM *)type->tp_alloc(type, 0);
  if (self != NULL){

  }

  return (PyObject *)self;

}

PyObject *VM_init(VM *self, PyObject *args, PyObject *kwds){
  // For the enviroment setup
  scm_init_guile();
  self->root = scm_current_module();
  self->SMOB_Tag = scm_make_smob_type("PythonSMOB", 0);
  self->callbacks = PyDict_New();
  
  return 0;
}


static PyObject *VM_set_callback(VM *self, PyObject *args){
  return 0;
}

static PyObject *VM_run_file(VM *self, PyObject *args){
  return 0;
}


PyMODINIT_FUNC initscheme(void){
    PyObject *m;

    m = Py_InitModule("scheme", SchemeMethods);
    if (m == NULL)
        return;

    SchemeError = PyErr_NewException("scheme.error", NULL, NULL);
    Py_INCREF(SchemeError);
    PyModule_AddObject(m, "error", SchemeError);
    
    VM_Type.tp_new = PyType_GenericNew;
    if (PyType_Ready(VM_Type) < 0)
        return;

    Py_INCREF(&VM_Type);
    PyModule_AddObject(m, "VM", (PyObject *)&VM_Type);
    
    
}
