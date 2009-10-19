from ctypes.util import find_library
from ctypes import *
import sys
import os.path

sys.path.append('/home/bluemoon/Sources/schemepy/')

from schemepy.types import *
from schemepy.exceptions import *

import types


lib = find_library("guile")

if lib is None:
    raise RuntimeError("Can't find a guile library to use.")

# Load the helper library which exports the macro's as C functions
path = os.path.abspath(os.path.join(os.path.split(__file__)[0], "_guilehelper.so"))
_guilehelper = cdll.LoadLibrary(path)


## Get the version from the helper
version_helper = (_guilehelper.guile_major_version(), _guilehelper.guile_minor_version())
ver_lib    = {(1, 6): '12', (1, 8): '17'}[version_helper]

if not lib.endswith(ver_lib):
    raise RuntimeError("The found library %s does not match the library the helper was compiled with." % lib)

guile = cdll.LoadLibrary(lib)

guile.scm_imp = _guilehelper.scm_imp
guile.scm_imp.argtypes = [c_void_p]
guile.scm_imp.restype = bool

#guile.scm_gc_protect_object.argtypes = [c_void_p]
#guile.scm_gc_protect_object.retype   = c_void_p

from _ctypes import Py_INCREF, Py_DECREF, PyObj_FromPtr

class SCMtbits(c_void_p):
	pass
    
class SCM(c_void_p):
    """
    A SCM hold a Scheme value.
    """
    def __init__(self, value=None):
        c_void_p.__init__(self)
        self.value = value
        
    def value_set(self, value):
        oldv = getattr(self, 'value', None)
        if oldv is not None and not guile.scm_imp(oldv):
            if getattr(self, 'protected', False):
                guile.scm_gc_unprotect_object(oldv)
            self.protected = False
        if value is not None and not guile.scm_imp(value):
            guile.scm_gc_protect_object(value)
            self.protected = True
        return c_void_p.value.__set__(self, value)

    def value_get(self):
        return c_void_p.value.__get__(self)
    value = property(value_get, value_set)
    
    def __del__(self):
        if guile is None:
            return # the guile library has been unloaded, do nothing
        self.value = None

    def __str__(self):
        return "<SCM %s>" % self.value
    
    def __repr__(self):
        return self.__str__()
    
    @staticmethod
    def toscm(val):
        """\
        Convert the Python value to a SCM

        Only some simple types are supported, user code should use
        vm.toscheme instead.
        """
        if type(val) is bool:
            return guile.scm_from_bool(val)
        if type(val) is int:
            return guile.scm_from_int32(val)
        if type(val) is float:
            return guile.scm_from_double(val)
        if type(val) is str:
            return guile.scm_from_locale_stringn(val, len(val))
        if type(val) is Symbol:
            name = SCM.toscm(val.name)
            return guile.scm_string_to_symbol(name)
        raise ConversionError(self, "Don't support conversion of a %s, use vm.toscheme instead." % val)


def exception_body_eval(src):
    """\
    The method is used to evaluate a piece of Scheme code where exception
    will be caught safely.
    """
    return guile.scm_eval_string(src).value

def exception_body_apply(arg):
    """\
    Apply a function in a context where exception will be caught.
    """
    return guile.scm_apply_0(guile.scm_car(arg), guile.scm_cdr(arg)).value

def exception_body_load(path):
    """\
    Load a Scheme script in a context where exception will be caught.
    """
    return guile.scm_primitive_load(path).value

exception_body_t = CFUNCTYPE(SCM, SCM)
exception_body_eval = exception_body_t(exception_body_eval)
exception_body_apply = exception_body_t(exception_body_apply)
exception_body_load = exception_body_t(exception_body_load)

def make_scheme_exception(vm, key, args):
    sym = vm.fromscheme(key)
    port = guile.scm_open_output_string()
    lst = vm.fromscheme(args, shallow=True)
    proc = vm.fromscheme(lst[0])
    if proc is False:
        proc = ""
    else:
        proc = "(in %s)" % proc
    
    guile.scm_simple_format(port, lst[1], lst[2])
    buf = guile.scm_get_output_string(port)
    guile.scm_close_port(port)
    
    msg = "%s%s raised: %s" % (sym, proc, vm.fromscheme(buf))
    Error = ScmMiscError

    if sym in ('error-signal', 'system-error', \
               'memory-allocation-error', 'stack-overflow'):
        Error = ScmSystemError
    elif sym == 'numerical-overflow':
        Error = ScmNumericalError
    elif sym == 'wrong-type-arg':
        Error = ScmWrongArgType
    elif sym == 'wrong-number-of-args':
        Error = ScmWrongArgNumber
    elif sym == 'read-error':
        Error = ScmSyntaxError
    elif sym == 'unbound-variable':
        Error = ScmUnboundVariable

    return Error(msg)
    
exception_handler_t = CFUNCTYPE(SCM, c_void_p, c_void_p, c_void_p)
def make_exception_handler(vm, exceptions):
    """\
    * error-signal: thrown after receiving an unhandled fatal
      signal such as SIGSEGV, SIGBUS, SIGFPE etc. The rest
      argument in the throw contains the coded signal number (at
      present this is not the same as the usual Unix signal
      number).
    
    * system-error: thrown after the operating system indicates an
      error condition. The rest argument in the throw contains the
      errno value.
    
    * numerical-overflow: numerical overflow.
    
    * out-of-range: the arguments to a procedure do not fall
      within the accepted domain.
    
    * wrong-type-arg: an argument to a procedure has the wrong
      type.
    
    * wrong-number-of-args: a procedure was called with the wrong
      number of arguments.
    
    * memory-allocation-error: memory allocation error.
    
    * stack-overflow: stack overflow error.
    
    * regular-expression-syntax: errors generated by the regular
      expression library.
    
    * misc-error: other errors. 
    """
    def exception_handle(trash, key, args):
        """\
        The callback handler of Scheme exception. It was implemented as
        a closure: the exception caught here will be append to the list
        of the closure variable `exceptions'.
        """
        key = SCM(key)
        args = SCM(args)
        exceptions.append(make_scheme_exception(vm, key, args))
        return guile.scm_bool_t().value

    return exception_handler_t(exception_handle)
        

guile.scm_internal_catch.argtypes = [SCM, exception_body_t, SCM, exception_handler_t, c_void_p]
guile.scm_internal_catch.restype = SCM
guile.scm_eval_string.argtypes = [SCM]
guile.scm_eval_string.restype  = SCM
guile.scm_c_eval_string.argtypes = [c_char_p]
guile.scm_c_eval_string.restype = SCM

guile.scm_c_lookup.argtypes = [SCM]
guile.scm_c_lookup.restype  = SCM

guile.scm_c_primitive_load.argtypes = [c_char_p]
guile.scm_c_primitive_load.restype = SCM


# Macros
guile.scm_unbndp = _guilehelper.scm_unbndp
guile.scm_bool_t = _guilehelper.scm_bool_t
guile.scm_bool_f = _guilehelper.scm_bool_f
guile.scm_eol    = _guilehelper.scm_eol
guile.scm_c_symbol_exists = _guilehelper.scm_c_symbol_exists
guile.scm_symbol_exists = _guilehelper.scm_symbol_exists

guile.scm_smob_data      = _guilehelper.scm_smob_data
guile.scm_set_smob_data  = _guilehelper.scm_set_smob_data
guile.scm_return_newsmob = _guilehelper.scm_return_newsmob
guile.scm_smob_predicate = _guilehelper.scm_smob_predicate

guile.scm_is_eol   = _guilehelper.scm_is_eol 
guile.scm_is_list  = _guilehelper.scm_is_list
guile.scm_is_alist = _guilehelper.scm_is_alist
guile.scm_is_exact = _guilehelper.scm_is_exact
guile.scm_is_fixnum = _guilehelper.scm_is_fixnum
# These are guile 1.8 functions
if hasattr(_guilehelper, 'scm_from_bool'):
	guile.scm_from_bool  = _guilehelper.scm_from_bool
	guile.scm_to_bool    = _guilehelper.scm_to_bool

	guile.scm_is_bool    = _guilehelper.scm_is_bool
	guile.scm_is_number  = _guilehelper.scm_is_number
	guile.scm_is_integer = _guilehelper.scm_is_integer
	guile.scm_is_rational= _guilehelper.scm_is_rational
	guile.scm_is_complex = _guilehelper.scm_is_complex 
	guile.scm_is_pair    = _guilehelper.scm_is_pair
	guile.scm_is_symbol  = _guilehelper.scm_is_symbol
	guile.scm_is_null    = _guilehelper.scm_is_null
	guile.scm_is_string  = _guilehelper.scm_is_string
	guile.scm_is_true    = _guilehelper.scm_is_true
	guile.scm_is_false    = _guilehelper.scm_is_false
        
	guile.scm_to_int32    = _guilehelper.scm_to_int32
	guile.scm_from_int32  = _guilehelper.scm_from_int32
	guile.scm_to_double   = _guilehelper.scm_to_double
	guile.scm_from_double = _guilehelper.scm_from_double

	guile.scm_to_locale_string    = _guilehelper.scm_to_locale_string
        guile.scm_to_locale_stringn    = _guilehelper.scm_to_locale_stringn
	guile.scm_from_locale_stringn = _guilehelper.scm_from_locale_stringn

	guile.scm_c_real_part = _guilehelper.scm_c_real_part
	guile.scm_c_imag_part = _guilehelper.scm_c_imag_part

	guile.scm_car = _guilehelper.scm_car
	guile.scm_cdr = _guilehelper.scm_cdr

	guile.scm_from_signed_integer = guile.scm_int2num
	guile.scm_from_locale_keyword = guile.scm_c_make_keyword

else:
	guile.scm_from_bool  = _guilehelper._scm_from_bool
#	guile.scm_is_bool    = _guilehelper._scm_is_bool
#	guile.scm_is_number  = _guilehelper._scm_is_number
#	guile.scm_is_integer = _guilehelper._scm_is_integer
#	guile.scm_is_pair    = _guilehelper._scm_is_pair
	guile.scm_is_symbol  = _guilehelper._scm_is_symbol
	guile.scm_is_true    = _guilehelper._scm_is_true
        guile.scm_is_false    = _guilehelper._scm_is_false
	guile.scm_is_null    = _guilehelper._scm_is_null


# Helper functions
guile.scm_c_real_part.argstypes = [SCM]
guile.scm_c_real_part.restype  = c_double
guile.scm_c_imag_part.argstypes = [SCM]
guile.scm_c_imag_part.restype  = c_double
guile.scm_bool_t.argstype = []
guile.scm_bool_t.restype  = SCM
guile.scm_bool_f.argstype = []
guile.scm_bool_f.restype  = SCM
guile.scm_eol.argtypes  = []
guile.scm_eol.restype   = SCM
guile.scm_cons.argtypes = [SCM, SCM]
guile.scm_cons.restype  = SCM
guile.scm_car.argtypes  = [SCM]
guile.scm_car.restype   = SCM
guile.scm_cdr.argtypes  = [SCM]
guile.scm_cdr.restype   = SCM

guile.scm_apply_0.argtypes = [SCM, SCM]
guile.scm_apply_0.restype = SCM
guile.scm_call_1.argtypes = [SCM, SCM]
guile.scm_call_1.restype = SCM

guile.scm_display.argtypes = [SCM, SCM]
guile.scm_display.restype  = None
guile.scm_newline.argtypes = [SCM]
guile.scm_display.restype  = None

guile.scm_make_smob_type.argtypes = [c_char_p, c_int]
guile.scm_make_smob_type.restype  = SCMtbits

guile.scm_return_newsmob.argtypes = [SCMtbits, c_void_p]
guile.scm_return_newsmob.restype  = SCM
guile.scm_smob_predicate.argtypes = [SCMtbits, SCM]
guile.scm_smob_predicate.restype  = bool

guile.scm_primitive_load.argtypes = [SCM]
guile.scm_primitive_load.restype = SCM

guile.scm_c_make_gsubr.argtypes = [c_char_p, c_int, c_int, c_int, c_void_p]
guile.scm_c_make_gsubr.restype  = SCM

guile.scm_set_procedure_property_x.argtypes = [SCM, SCM, SCM]
guile.scm_set_procedure_property_x.restype = SCM
guile.scm_procedure_property.argtypes = [SCM, SCM]
guile.scm_procedure_property.restype = SCM

guile.scm_define.argtypes = [SCM, SCM]

guile.scm_define.restype = SCM
guile.scm_variable_ref.argtypes = [SCM]
guile.scm_variable_ref.restype  = SCM
guile.scm_lookup.argtypes = [SCM]
guile.scm_lookup.restype = SCM
guile.scm_symbol_exists.argtypes = [SCM]
guile.scm_symbol_exists.restype = bool

guile.scm_current_module.restype = SCM
guile.scm_set_current_module.argtypes = [SCM]
guile.scm_set_current_module.restype = SCM

guile.scm_open_output_string.argtypes = []
guile.scm_open_output_string.restype = SCM
guile.scm_simple_format.argtypes = [SCM, SCM, SCM]
guile.scm_simple_format.restype = SCM
guile.scm_get_output_string.argtypes = [SCM]
guile.scm_get_output_string.restype = SCM
guile.scm_close_port.argtypes = [SCM]
guile.scm_close_port.restype = SCM

# Predict functions
guile.scm_exact_p.argtypes = [SCM]
guile.scm_exact_p.restype = SCM
guile.scm_is_true.argtypes     = [SCM]
guile.scm_is_true.restype      = int
guile.scm_is_false.argtypes     = [SCM]
guile.scm_is_false.restype      = int
guile.scm_is_bool.argstype     = [SCM]
guile.scm_is_bool.restype      = bool
guile.scm_is_number.argstype   = [SCM]
guile.scm_is_number.restype    = bool
guile.scm_is_fixnum.argstype   = [SCM]
guile.scm_is_fixnum.restype    = bool
guile.scm_is_integer.argstype  = [SCM]
guile.scm_is_integer.restype   = bool
guile.scm_is_rational.argstype = [SCM]
guile.scm_is_rational.restype  = bool
guile.scm_is_complex.argstype  = [SCM]
guile.scm_is_complex.restype   = bool
guile.scm_is_string.argstype   = [SCM]
guile.scm_is_string.restype    = bool
guile.scm_is_pair.argstype     = [SCM]
guile.scm_is_pair.restype      = bool
guile.scm_is_symbol.argstype   = [SCM]
guile.scm_is_symbol.restype    = bool
guile.scm_is_list.argtypes  = [SCM]
guile.scm_is_list.restype   = bool
guile.scm_is_alist.argtypes = [SCM]
guile.scm_is_alist.restype  = bool
guile.scm_is_null.argtypes  = [SCM]
guile.scm_is_null.restype   = bool
guile.scm_is_eol.argtypes   = [SCM]
guile.scm_is_eol.restype    = bool
guile.scm_procedure_p.argtypes = [SCM]
guile.scm_procedure_p.restype = SCM

# Conversion functions
guile.scm_from_int32.argtypes = [c_int]
guile.scm_from_int32.restype = SCM
guile.scm_make_complex.argtypes = [c_double, c_double]
guile.scm_make_complex.restype = SCM
guile.scm_from_double.argtypes = [c_double]
guile.scm_from_double.restype = SCM
guile.scm_to_double.argstypes   = [SCM]
guile.scm_to_double.restype    = c_double
guile.scm_from_bool.argtypes   = [c_int]
guile.scm_from_bool.restype    = SCM
guile.scm_to_locale_string.argtypes = [SCM]
guile.scm_to_locale_string.restype  = c_char_p

guile.scm_from_locale_stringn.argtypes  = [c_char_p, c_int]
guile.scm_from_locale_stringn.restype   = SCM
guile.scm_to_locale_stringn.argtypes = [SCM, POINTER(c_ulong)]
guile.scm_to_locale_stringn.restype = c_void_p
guile.scm_number_to_string.argtypes = [SCM, SCM]
guile.scm_number_to_string.restype = SCM
guile.scm_symbol_to_string.argtypes = [SCM]
guile.scm_symbol_to_string.restype = SCM
guile.scm_string_to_symbol.argtypes = [SCM]
guile.scm_string_to_symbol.restype = SCM

def scm_py_call(py_callable, shallow, vm, scm_args):
    """\
    This function will be registered to the Scheme world to call a Python
    callable.
    
    py_callable is a Python callable, wrapped as a SMOB in Scheme world.
    shallow     is whether the wrap is shallow, i.e. the args and return values
                will be auto-converted if not shallow.
    vm          is the vm in which to call the function.
    scm_args    is a Scheme cons-list for the function.

    This function will not be available to normal Scheme code.
    """
    vm = PythonSMOB.get(vm)
    py_callable, shallow = vm.fromscheme(py_callable), vm.fromscheme(shallow)
    args = vm.fromscheme(scm_args, shallow=shallow)
    result = py_callable(*args)
    if not shallow:
        result = vm.toscheme(result)
    else:
        if not isinstance(result, SCM):
            # TODO: is it safe to raise exception in a C handler?
            raise TypeError("Return type is not a SCM!")
    return result.value

scm_py_call_t = CFUNCTYPE(SCM, SCM, SCM, SCM, SCM)
scm_py_call = scm_py_call_t(scm_py_call)


class VM(object):
    """VM for guile.
    """

    def __init__(self, profile):
        """\
        Create a VM.
        """
        env = profiles.get(profile)
        if not env:
            raise ProfileNotFoundError("No such profile %s" % profile)
        
        post_hook = None
        if isinstance(env, tuple):
            env, post_hook = env
            
        global guileroot
        guile.scm_set_current_module(guileroot)
        self.module = guile.scm_call_1(makescope, env)
        self._init_pyfunc_interface()

        if post_hook:
            post_hook(self)

    def compile(self, code):
        """Compile for guile. Guile doesn't support bytecode yet. So
        just do nothing."""
        return code

    def ensure_scope(meth):
        """\
        The decorator to ensure the scope of guile
        is set to the current module of VM before
        each access to the scope.
        """
        def scoped_meth(self, *args, **kw):
            guile.scm_set_current_module(self.module)
            return meth(self, *args, **kw)
        return scoped_meth

    def catch_exception_do(self, action, arg):
        """\
        Do action with exception handler. If exception thrown in Guile, catch
        it and re-throw in Python.
        """
        exceptions = []
        r = guile.scm_internal_catch(guile.scm_bool_t(), action, arg,
                                     make_exception_handler(self, exceptions), None)
        if len(exceptions) != 0:
            raise exceptions[0]
        return r

    @ensure_scope
    def define(self, name, value):
        """\
        Define a variable in Scheme. Similar to Scheme code
          (define name value)

          name can either be a string or a schemepy.types.Symbol
          value should be a Scheme value
        """
        if not isinstance(value, SCM):
            raise TypeError, "Value to define should be a Scheme value."
        
        name = Symbol(name)
        guile.scm_define(self.toscheme(name), value)

    @ensure_scope
    def get(self, name, default=None):
        """\
        Get the value bound to the symbol.

          name can either be a string or a schemepy.types.Symbol
        """
        name = Symbol(name)
        if not guile.scm_symbol_exists(self.toscheme(name)):
            return default
        return guile.scm_variable_ref(guile.scm_lookup(self.toscheme(name)))

    @ensure_scope
    def load(self, filename):
        """\
        Load a scheme script file.
        """
        
        self.catch_exception_do(exception_body_load, self.toscheme(filename))

    @ensure_scope
    def eval(self, src):
        """\
        Eval a piece of compiled Scheme code.
        """
        return self.catch_exception_do(exception_body_eval, self.toscheme(src))

    @ensure_scope
    def apply(self, proc, args):
        """\
        Call the Scheme procedure proc with args as arguments.

          proc should be a Scheme procedure
          args should be a list os Scheme value

        The return value is a Scheme value.
        """
        arglist = guile.scm_eol()
        for arg in reversed(args):
            arglist = guile.scm_cons(arg, arglist)

        return self.catch_exception_do(exception_body_apply,
                                       guile.scm_cons(proc, arglist))

    @ensure_scope
    def repl(self):
        "Enter the read-eval-print loop."
        guile.scm_c_eval_string("(top-repl)")

    @ensure_scope
    def toscheme(self, val, shallow=False):
        "Convert a Python value to a Scheme value."
        if type(val) is bool:
            return guile.scm_from_bool(val)
        if type(val) is int:
            return guile.scm_from_int32(val)
        if type(val) is complex:
            return guile.scm_make_complex(val.real, val.imag)
        if type(val) is float:
            return guile.scm_from_double(val)
        if type(val) is Cons:
            if shallow:
                if type(val.car) is not SCM or type(val.cdr) is not SCM:
                    raise ConversionError(val, "Invalid shallow conversion on Cons, both car and cdr should be a Scheme value.")
                return guile.scm_cons(var.car, var.cdr)
            return guile.scm_cons(self.toscheme(val.car), self.toscheme(val.cdr))
        if isinstance(val, list):
            scm = guile.scm_eol()
            for item in reversed(val):
                if shallow:
                    if type(item) is not SCM:
                        raise ConversionError(val, "Invalid shallow conversion on list, every element should be a Scheme value.")
                    scm = guile.scm_cons(item, scm)
                else:
                    scm = guile.scm_cons(self.toscheme(item), scm)
            return scm
        if isinstance(val, dict):
            scm = guile.scm_eol()
            for key, value in val.iteritems():
                if shallow:
                    if type(value) is not SCM:
                        raise ConversionError(val, "Invalid shallow conversion on dict, every value should be a Scheme value.")
                    scm = guile.scm_cons(guile.scm_cons(self.toscheme(key), value), scm)
                else:
                    scm = guile.scm_cons(guile.scm_cons(self.toscheme(key), self.toscheme(value)), scm)
            return scm
        if type(val) is str:
            return guile.scm_from_locale_stringn(val, len(val))
        if type(val) is unicode:
            try:
                s = str(val)
                return guile.scm_from_locale_stringn(s, len(s))
            except UnicodeEncodeError:
                pass
        if type(val) is long:
            s = str(val)
            return guile.scm_c_eval_string(s)
        if type(val) is Symbol:
            name = self.toscheme(val.name)
            return guile.scm_string_to_symbol(name)
        if type(val) is Lambda:
            return val._lambda
        if callable(val):
            smob = PythonSMOB.new(val)
            lam = self.apply(self._scm_lambda_wrapper, [self._scm_py_call,
                                                        smob,
                                                        self.toscheme(shallow),
                                                        self.toscheme(self)])

            guile.scm_set_procedure_property_x(lam,
                                               self._scm_py_lambda_identifier,
                                               smob)
            return lam
        return PythonSMOB.new(val)

    @ensure_scope
    def fromscheme(self, val, shallow=False):
        "Get a Python value from a Scheme value."
        if not isinstance(val, SCM):
            raise ArgumentError("Expecting a Scheme value, but get a %s." % val)
        
        if guile.scm_is_bool(val):
            if guile.scm_is_true(val):
                return True
            return False
        
        if guile.scm_is_number(val):
            if guile.scm_is_true(guile.scm_exact_p(val)):
                if guile.scm_is_fixnum(val):
                    return guile.scm_to_int32(val)
                if guile.scm_is_integer(val):
                    s = guile.scm_number_to_string(val, self.toscheme(10))
                    return eval(self.fromscheme(s))
                return guile.scm_to_double(val) # rational
            if guile.scm_c_imag_part(val) != 0:
                return complex(guile.scm_c_real_part(val),
                               guile.scm_c_imag_part(val))
            return guile.scm_to_double(val)
        
        if guile.scm_is_eol(val):
            return []

        if guile.scm_is_pair(val):
            if guile.scm_is_list(val):
                l = []
                scm = val
                while not guile.scm_is_null(scm):
                    item = guile.scm_car(scm)
                    if not shallow:
                        scheme = self.fromscheme(item)
                        l.append(scheme)
                    else:
                        l.append(item)

                    scm = guile.scm_cdr(scm)
                return l
            
            else:
                car = guile.scm_car(val)
                cdr = guile.scm_cdr(val)
                if not shallow:
                    return Cons(self.fromscheme(car), self.fromscheme(cdr))
                else:
                    return Cons(car, cdr)
                
        if guile.scm_is_eol(val):
            return []
        
        if guile.scm_is_symbol(val):
            symbol = Symbol(self.fromscheme(guile.scm_symbol_to_string(val)))
            return str(symbol)
        
        if guile.scm_is_string(val):
            # FIXME: This is leaking memory
            len = c_ulong(0)
            mem = guile.scm_to_locale_stringn(val, pointer(len))
            return string_at(mem, len.value)

        if guile.scm_is_true(guile.scm_procedure_p(val)):
            smob = guile.scm_procedure_property(val,
                                                self._scm_py_lambda_identifier)
            if guile.scm_is_false(smob):
                return Lambda(val, self, shallow)
            return self.fromscheme(smob) # get the original callable
        
        if guile.scm_smob_predicate(PythonSMOB.tag, val):
            return PythonSMOB.get(val)
        
        raise ConversionError(val, "Don't know how to convert this type.")

    @ensure_scope
    def type(self, val):
        """\
        Get the (Python) type of the value.

        NOTE: the type is not necessarily the *real* type of
              the converted Python value. In other words,
              `vm.type(scm) == vm.fromscheme(scm)' might be
              false. But `type(vm.fromscheme(scm))' will be at
              least a sub-type of `vm.type(scm)'.
        """
        if guile.scm_is_bool(val):
            return bool
        if guile.scm_is_number(val):
            if guile.scm_is_true(guile.scm_exact_p(val)):
                if guile.scm_is_fixnum(val):
                    return int
                if guile.scm_is_integer(val):
                    return long
                return float
            if guile.scm_c_imag_part(val) != 0:
                return complex
            return float
        if guile.scm_is_eol(val):
            return list
        if guile.scm_is_pair(val):
            if guile.scm_is_list(val):
                if guile.scm_is_alist(val):
                    return dict
                else:
                    return list
            else:
                return Cons
        if guile.scm_is_eol(val):
            return list
        if guile.scm_is_symbol(val):
            return Symbol
        if guile.scm_is_string(val):
            return str
        if guile.scm_is_true(guile.scm_procedure_p(val)):
            smob = guile.scm_procedure_property(val,
                                                self._scm_py_lambda_identifier)
            if guile.scm_is_false(smob):
                return Lambda
            return types.FunctionType
        
        if guile.scm_smob_predicate(PythonSMOB.tag, val):
            return object
        
        return type(None)
        
    def _init_pyfunc_interface(self):
        """\
        Do necessary initializations so that a Python callable can
        be wrapped as a Scheme lambda.
        """
        self._scm_lambda_wrapper = guile.scm_c_eval_string("""
            (lambda (call-py py-callable shallow vm)
              (lambda args
                (call-py py-callable shallow vm args)))""")
        self._scm_py_call = guile.scm_c_make_gsubr("scm-py-call", 4, 0, 0,
                                                   scm_py_call)
        self._scm_py_lambda_identifier = SCM.toscm(Symbol("#{schemepy python callable}#"))


class PythonSMOB(c_void_p):
	"""
	Functions for dealing with a Python "pass-thru" object.
	"""
	def register():
		# Create the SMOB type
		PythonSMOB.tag = guile.scm_make_smob_type("PythonSMOB", 0)
		guile.scm_set_smob_free( PythonSMOB.tag, PythonSMOB.free)
		guile.scm_set_smob_print(PythonSMOB.tag, PythonSMOB.str)
                
	register = staticmethod(register)	

        @staticmethod
	def new(pyobj):
		"""
		Create a new PythonSMOB which wraps the given object.
		"""
		pypointer = id(pyobj)	

		# Increase the reference count to the object	
		Py_INCREF(pyobj)

		# Create the new smob
		return guile.scm_return_newsmob(PythonSMOB.tag, pypointer)

        @staticmethod
	def free(smob):
		"""
		When the guile garbage collector frees the smob, remove the 
		extra reference so Python can garbage collect the object.
		"""
		#print "PythonSMOB.free"

		# Get the python object we are pointing too
		pypointer = guile.scm_smob_data(smob)

		# Decrease the reference to the pypointer
		Py_DECREF(PyObj_FromPtr(pypointer))

		return 0
            
	free_cfunc = CFUNCTYPE(c_int, c_void_p)

        @staticmethod
	def str(smob, port, pstate):
		smob, port = SCM(smob), SCM(port)

		# Get the python object we are pointing too
		pypointer = guile.scm_smob_data(smob)

		pyobj = PyObj_FromPtr(pypointer)
		guile.scm_display(SCM.toscm(repr(pyobj)), port)
		guile.scm_newline(port)

	str_cfunc = CFUNCTYPE(None, c_void_p, c_void_p, c_void_p)

        @staticmethod
	def get(smob):
		pyPointer = guile.scm_smob_data(smob)
		return PyObj_FromPtr(pyPointer)

PythonSMOB.free = PythonSMOB.free_cfunc(PythonSMOB.free)
PythonSMOB.str  = PythonSMOB.str_cfunc(PythonSMOB.str)

guile.scm_set_smob_free.argtypes  = [SCMtbits, PythonSMOB.free_cfunc]
guile.scm_set_smob_free.restype   = None
guile.scm_set_smob_print.argtypes = [SCMtbits, PythonSMOB.str_cfunc]
guile.scm_set_smob_print.restype  = None



# Initialize guile
guile.scm_init_guile()
guileroot = guile.scm_current_module()

# Load the pretty-print module..
guile.scm_c_eval_string("(use-modules (ice-9 pretty-print))")
prettyprint_symbol = guile.scm_c_lookup("pretty-print")
prettyprint        = guile.scm_variable_ref(prettyprint_symbol)

# Create a "scope" for this class
#__file__ = os.path.realpath(__file__)
__path__ = os.path.dirname(__file__)

guile.scm_c_primitive_load(os.path.join(__path__, "profiles", "scope.scm"))
makescope_symbol = guile.scm_c_lookup("make-scope")
makescope        = guile.scm_variable_ref(makescope_symbol)

# Profiles
guile.scm_c_eval_string("(use-modules (ice-9 r5rs))")
profiles = {
    "r5rs" : guile.scm_c_eval_string("(scheme-report-environment 5)"),
    "minimal" : guile.scm_c_eval_string("(null-environment 5)"),
    }



# Register Python smob
PythonSMOB.register()
        
    
