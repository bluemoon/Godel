#include "Python.h"
#include "scheme.h"
#include "structmember.h"
typedef struct {
  PyObject_HEAD
  PyObject *callbacks;
  Scheme_Env *env;

} scheme;


static PyMemberDef scheme_members[] = {
  {"callbacks", T_OBJECT_EX, offsetof(scheme, callbacks), 0, "callback dictionary"},
  {NULL}  /* Sentinel */
};


// functions to create/destroy scheme
static void scheme_dealloc(scheme *self);
static PyObject *scheme_new(PyTypeObject *type, PyObject *args, PyObject *kwds);
PyObject *scheme_init(scheme *self, PyObject *args, PyObject *kwds);

// method functions in scheme
static PyObject *scheme_set_callback(scheme *self, PyObject *args);
static PyObject *scheme_run_file(scheme *self, PyObject *args);

static Scheme_Object *scheme_callback(int argc, Scheme_Object *argv[]);
static PyMethodDef SchemeMethods[] = {
  {NULL, NULL, 0, NULL},
};

static PyMethodDef scheme_methods[] = {
    {"set_callback", (PyCFunction)scheme_set_callback, METH_VARARGS, ""},
    {"run_file", (PyCFunction)scheme_run_file, METH_VARARGS, ""},
    {NULL, NULL, 0, NULL}  /* Sentinel */
};




static PyTypeObject scheme_Type = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "scheme.scheme",             /*tp_name*/
    sizeof(scheme),             /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)scheme_dealloc, /*tp_dealloc*/
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
    "scheme objects",           /* tp_doc */
    0,		               /* tp_traverse */
    0,		               /* tp_clear */
    0,		               /* tp_richcompare */
    0,		               /* tp_weaklistoffset */
    0,		               /* tp_iter */
    0,		               /* tp_iternext */
    scheme_methods,             /* tp_methods */
    scheme_members,             /* tp_members */
    //0,
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)scheme_init,      /* tp_init */
    0,                         /* tp_alloc */
    scheme_new,                 /* tp_new */
};


