#include "Python.h"
#include "structmember.h"
#include <libguile.h>

typedef struct {
  PyObject_HEAD
  PyObject *callbacks;
  SCM *root;
  SCM *SMOB_Tag;

} VM;


static PyMemberDef VM_members[] = {
  {"callbacks", T_OBJECT_EX, offsetof(scheme, callbacks), 0, "callback dictionary"},
  {NULL}  /* Sentinel */
};


// functions to create/destroy scheme
static void VM_dealloc(VM *self);
static PyObject *VM_new(PyTypeObject *type, PyObject *args, PyObject *kwds);
PyObject *VM_init(VM *self, PyObject *args, PyObject *kwds);

// method functions in scheme
static PyObject *VM_set_callback(VM *self, PyObject *args);
static PyObject *VM_run_file(VM *self, PyObject *args);

static Scheme_Object *VM_callback(int argc, Scheme_Object *argv[]);
static PyMethodDef SchemeMethods[] = {
  {NULL, NULL, 0, NULL},
};

static PyMethodDef VM_methods[] = {
    {"set_callback", (PyCFunction)VM_set_callback, METH_VARARGS, ""},
    {"run_file", (PyCFunction)VM_run_file, METH_VARARGS, ""},
    {NULL, NULL, 0, NULL}  /* Sentinel */
};



static PyTypeObject VM_Type = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "scheme.VM",             /*tp_name*/
    sizeof(VM),             /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)VM_dealloc, /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    "VM objects",           /* tp_doc */
    0,		               /* tp_traverse */
    0,		               /* tp_clear */
    0,		               /* tp_richcompare */
    0,		               /* tp_weaklistoffset */
    0,		               /* tp_iter */
    0,		               /* tp_iternext */
    VM_methods,             /* tp_methods */
    VM_members,             /* tp_members */
    //0,
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)VM_init,      /* tp_init */
    0,                         /* tp_alloc */
    VM_new,                 /* tp_new */
};


