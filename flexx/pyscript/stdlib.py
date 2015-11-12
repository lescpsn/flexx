"""
PyScript standard functions.

"""

# Functions not covered by this lib:
# isinstance, issubclass, print, len, max, min, callable, chr, ord

FUNCTIONS = {}
METHODS = {}
FUNCTION_PREFIX = 'py_'
METHOD_PREFIX = '_py_'

IMPORT_PREFIX = 'py_'
IMPORT_DOT = '__'

def get_partial_std_lib(func_names, method_names, imported_objects, indent=0):
    """ Get the code for the PyScript standard library consisting of
    the given function and method names. The given indent specifies how
    many sets of 4 spaces to prepend.
    """
    lines = []
    for name in sorted(func_names):
        code = FUNCTIONS[name].strip()
        lines.append('var %s%s = %s;' % (FUNCTION_PREFIX, name, code))
    for name in sorted(method_names):
        code = METHODS[name].strip()
        lines.append('Object.prototype.%s%s = %s;' % (METHOD_PREFIX, name, code))
    for name in sorted(imported_objects):
        if IMPORTS[name] is None:
            continue
        code = IMPORTS[name].strip()
        name = name.replace('.', IMPORT_DOT)
        lines.append('var %s%s = %s;' % (IMPORT_PREFIX, name, code))
    code = '\n'.join(lines)
    if indent:
        lines = ['    '*indent + line for line in code.splitlines()]
        code = '\n'.join(lines)
    return code

def get_full_std_lib(indent=0):
    """ Get the code for the full PyScript standard library.
    
    The given indent specifies how many sets of 4 spaces to prepend.
    If the full stdlib is made available in JavaScript, multiple
    snippets of code can be transpiled without inlined stdlib parts by
    using ``py2js(..., inline_stdlib=False)``.
    """
    return get_partial_std_lib(FUNCTIONS.keys(), METHODS.keys(), IMPORTS.keys(), indent)

## ----- Functions

## Hardcore functions

FUNCTIONS['hasattr'] = """function (ob, name) { // nargs: 2
    return (ob !== undefined) && (ob !== null) && (ob[name] !== undefined);
}"""

FUNCTIONS['getattr'] = """function (ob, name, deflt) { // nargs: 2 3
    var has_attr = ob !== undefined && ob !== null && ob[name] !== undefined;
    if (has_attr) {return ob[name];}
    else if (deflt !== undefined) {return deflt;}
    else {var e = Error(name); e.name='AttributeError'; throw e;}
}"""

FUNCTIONS['setattr'] = """function (ob, name, value) {  // nargs: 3
    ob[name] = value;
}"""

FUNCTIONS['delattr'] = """function (ob, name) {  // nargs: 2
    delete ob[name];
}"""

FUNCTIONS['dict'] = """function (x) {
    var t, i, keys, r={};
    if (Array.isArray(x)) {
        for (i=0; i<x.length; i++) {
            t=x[i]; r[t[0]] = t[1];
        }
    } else {
        keys = Object.keys(x);
        for (i=0; i<keys.length; i++) {
            t=keys[i]; r[t] = x[t];
        }
    }
    return r;
}"""

FUNCTIONS['list'] = """function (x) {
    var r=[];
    if (typeof x==="object" && !Array.isArray(x)) {x = Object.keys(x)}
    for (var i=0; i<x.length; i++) {
        r.push(x[i]);
    }
    return r;
}"""

FUNCTIONS['range'] = """function (start, end, step) {
var i, res = [];
    var val = start;
    var n = (end - start) / step;
    for (i=0; i<n; i++) {
        res.push(val);
        val += step;
    }
    return res;
}"""


## Normal functions

FUNCTIONS['pow'] = 'Math.pow // nargs: 2'

FUNCTIONS['sum'] = """function (x) {  // nargs: 1
    return x.reduce(function(a, b) {return a + b;});
}"""

FUNCTIONS['round'] = 'Math.round // nargs: 1'

FUNCTIONS['int'] = """function (x) { // nargs: 1
    return x<0 ? Math.ceil(x): Math.floor(x);
}"""

FUNCTIONS['float'] = 'Number // nargs: 1'

FUNCTIONS['str'] = 'String // nargs: 0 1'

FUNCTIONS['repr'] = 'JSON.stringify // nargs: 1'

FUNCTIONS['bool'] = """function (x) { // nargs: 1
    return Boolean(FUNCTION_PREFIXtruthy(x));
}"""

FUNCTIONS['abs'] = 'Math.abs // nargs: 1'

FUNCTIONS['divmod'] = """function (x, y) { // nargs: 2
    var m = x % y; return [(x-m)/y, m];
}"""

FUNCTIONS['all'] = """function (x) { // nargs: 1
    for (var i=0; i<x.length; i++) {
        if (!FUNCTION_PREFIXtruthy(x[i])){return false}
    } return true;
}"""

FUNCTIONS['any'] = """function (x) { // nargs: 1
    for (var i=0; i<x.length; i++) {
        if (FUNCTION_PREFIXtruthy(x[i])){return true}
    } return false;
}"""

FUNCTIONS['enumerate'] = """function (iter) { // nargs: 1
    var i, res=[];
    if ((typeof iter==="object") && (!Array.isArray(iter))) {iter = Object.keys(iter);}
    for (i=0; i<iter.length; i++) {res.push([i, iter[i]]);}
    return res;
}"""
        
FUNCTIONS['zip'] = """function () { // nargs: 2 3 4 5 6 7 8 9
    var i, j, tup, arg, args = [], res = [], len = 1e20;
    for (i=0; i<arguments.length; i++) {
        arg = arguments[i];
        if ((typeof arg==="object") && (!Array.isArray(arg))) {arg = Object.keys(arg);}
        args.push(arg);
        len = Math.min(len, arg.length);
    }
    for (j=0; j<len; j++) {
        tup = []
        for (i=0; i<args.length; i++) {tup.push(args[i][j]);}
        res.push(tup);
    }
    return res;
}"""

FUNCTIONS['reversed'] = """function (iter) { // nargs: 1
    if ((typeof iter==="object") && (!Array.isArray(iter))) {iter = Object.keys(iter);}
    return iter.slice().reverse();
}"""

FUNCTIONS['sorted'] = """function (iter, key, reverse) { // nargs: 1 2 3
    if ((typeof iter==="object") && (!Array.isArray(iter))) {iter = Object.keys(iter);}
    var comp = function (a, b) {return key(a) - key(b);};
    comp = Boolean(key) ? comp : undefined; 
    iter = iter.slice().sort(comp);
    if (reverse) iter.reverse();
    return iter;
}"""

FUNCTIONS['filter'] = """function (func, iter) { // nargs: 2
    if (typeof func === "undefined" || func === null) {func = function(x) {return x;}}
    if ((typeof iter==="object") && (!Array.isArray(iter))) {iter = Object.keys(iter);}
    return iter.filter(func);
}"""

FUNCTIONS['map'] = """function (func, iter) { // nargs: 2
    if (typeof func === "undefined" || func === null) {func = function(x) {return x;}}
    if ((typeof iter==="object") && (!Array.isArray(iter))) {iter = Object.keys(iter);}
    return iter.map(func);
}"""

## Other / Helper functions

FUNCTIONS['truthy'] = """function (v) {
    if (v === null || typeof v !== "object") {return v;}
    else if (v.length !== undefined) {return v.length ? v : false;}
    else if (v.byteLength !== undefined) {return v.byteLength ? v : false;} 
    else {return Object.getOwnPropertyNames(v).length ? v : false;}
}"""

FUNCTIONS['equals'] = """function equals (a, b) { // nargs: 2
    if (a == null || b == null) {
    } else if (Array.isArray(a) && Array.isArray(b)) {
        var i = 0, iseq = a.length == b.length;
        while (iseq && i < a.length) {iseq = equals(a[i], b[i]); i+=1;}
        return iseq;
    } else if (a.constructor === Object && b.constructor === Object) {
        var akeys = Object.keys(a), bkeys = Object.keys(b);
        akeys.sort(); bkeys.sort();
        var i=0, k, iseq = equals(akeys, bkeys);
        while (iseq && i < akeys.length) {k=akeys[i]; iseq = equals(a[k], b[k]); i+=1;}
        return iseq;
    } return a == b;
}"""

FUNCTIONS['contains'] = """function contains (a, b) { // nargs: 2
    if (b == null) {
    } else if (Array.isArray(b)) {
        for (var i=0; i<b.length; i++) {if (FUNCTION_PREFIXequals(a, b[i]))
                                           return true;}
        return false;
    } else if (b.constructor === Object) {
        for (var k in b) {if (a == k) return true;}
        return false;
    } else if (b.constructor == String) {
        return b.indexOf(a) >= 0;
    } var e = Error('Not a container: ' + b); e.name='TypeError'; throw e;
}"""

FUNCTIONS['add'] = """function (a, b) { // nargs: 2
    if (Array.isArray(a) && Array.isArray(b)) {
        return a.concat(b);
    } return a + b;
}"""

FUNCTIONS['mult'] = """function (a, b) { // nargs: 2
    if ((typeof a === 'number') + (typeof b === 'number') === 1) {
        if (a.constructor === String) return a.repeat(b);
        if (b.constructor === String) return b.repeat(a);
        if (Array.isArray(b)) {var t=a; a=b; b=t;}
        if (Array.isArray(a)) {
            var res = []; for (var i=0; i<b; i++) res = res.concat(a);
            return res;
        }
    } return a * b;
}"""

FUNCTIONS['time'] = """function () {return new Date().getTime() / 1000;}"""

FUNCTIONS['perf_counter'] = """function() {
    if (typeof(process) === "undefined"){return performance.now()*1e-3;}
    else {var t = process.hrtime(); return t[0] + t[1]*1e-9;}
}"""  # Work in nodejs and browser


## ----- Methods

## List only

METHODS['append'] = """function (x) { // nargs: 1
    if (!Array.isArray(this)) return this.KEY.apply(this, arguments);
    this.push(x);
}"""

METHODS['extend'] = """function (x) { // nargs: 1
    if (!Array.isArray(this)) return this.KEY.apply(this, arguments);
    this.push.apply(this, x);   
}"""

METHODS['insert'] = """function (i, x) { // nargs: 2
    if (!Array.isArray(this)) return this.KEY.apply(this, arguments);
    i = (i < 0) ? this.length + i : i;
    this.splice(i, 0, x);
}"""

METHODS['remove'] = """function (x) { // nargs: 1
    if (!Array.isArray(this)) return this.KEY.apply(this, arguments);
    for (var i=0; i<this.length; i++) {
        if (FUNCTION_PREFIXequals(this[i], x)) {this.splice(i, 1); return;}
    }
    var e = Error(x); e.name='ValueError'; throw e;
}"""

METHODS['reverse'] = """function () { // nargs: 0
    this.reverse();
}"""

METHODS['sort'] = """function (key, reverse) { // nargs: 0 1 2
    if (!Array.isArray(this)) return this.KEY.apply(this, arguments);
    var comp = function (a, b) {return key(a) - key(b);};
    comp = Boolean(key) ? comp : undefined; 
    this.sort(comp);
    if (reverse) this.reverse();
}"""

## List and dict

METHODS['clear'] = """function () { // nargs: 0
    if (Array.isArray(this)) {
        this.splice(0, this.length);
    } else if (this.constructor === Object) {
        var keys = Object.keys(this);
        for (var i=0; i<keys.length; i++) delete this[keys[i]];
    } else return this.KEY.apply(this, arguments);
}"""

METHODS['copy'] = """function () { // nargs: 0
    if (Array.isArray(this)) {
        return this.slice(0);
    } else if (this.constructor === Object) {
        var key, keys = Object.keys(this), res = {};
        for (var i=0; i<keys.length; i++) {key = keys[i]; res[key] = this[key];}
        return res;
    } else return this.KEY.apply(this, arguments);
}"""

METHODS['pop'] = """function (i, d) { // nargs: 1 2
    if (Array.isArray(this)) {
        i = (i === undefined) ? -1 : i;
        i = (i < 0) ? (this.length + i) : i;
        var popped = this.splice(i, 1);
        if (popped.length)  return popped[0];
        var e = Error(i); e.name='IndexError'; throw e;
    } else if (this.constructor === Object) {
        var res = this[i]
        if (res !== undefined) {delete this[i]; return res;}
        else if (d !== undefined) return d;
        var e = Error(i); e.name='KeyError'; throw e;
    } else return this.KEY.apply(this, arguments);
}"""

## List and str

# start and stop nor supported for list on Python, but for simplicity, we do
METHODS['count'] = """function (x, start, stop) { // nargs: 1 2 3
    start = (start === undefined) ? 0 : start;
    stop = (stop === undefined) ? this.length : stop;
    start = Math.max(0, ((start < 0) ? this.length + start : start));
    stop = Math.min(this.length, ((stop < 0) ? this.length + stop : stop));
    if (Array.isArray(this)) {
        var count = 0;
        for (var i=0; i<this.length; i++) { 
            if (FUNCTION_PREFIXequals(this[i], x)) {count+=1;}
        } return count;
    } else if (this.constructor == String) {
        var count = 0, i = start;
        while (i >= 0 && i < stop) {
            i = this.indexOf(x, i);
            if (i < 0) break; 
            count += 1;
            i += Math.max(1, x.length);
        } return count;
    } else return this.KEY.apply(this, arguments);
}"""

METHODS['index'] = """function (x, start, stop) { // nargs: 1 2 3
    start = (start === undefined) ? 0 : start;
    stop = (stop === undefined) ? this.length : stop;
    start = Math.max(0, ((start < 0) ? this.length + start : start));
    stop = Math.min(this.length, ((stop < 0) ? this.length + stop : stop));
    if (Array.isArray(this)) {
        for (var i=start; i<stop; i++) {
            if (FUNCTION_PREFIXequals(this[i], x)) {return i;} // indexOf cant do this
        }
    } else if (this.constructor === String) {
        var i = this.slice(start, stop).indexOf(x);
        if (i >= 0) return i + start;
    } else return this.KEY.apply(this, arguments);
    var e = Error(x); e.name='ValueError'; throw e;
}"""

## Dict only

# note: fromkeys is a classmethod, and we dont support it.

METHODS['get'] = """function (key, d) { // nargs: 1 2
    if (this.constructor !== Object) return this.KEY.apply(this, arguments);
    if (this[key] !== undefined) {return this[key];}
    else if (d !== undefined) {return d;}
    else {return null;}
}"""

METHODS['items'] = """function () { // nargs: 0
    if (this.constructor !== Object) return this.KEY.apply(this, arguments);
    var key, keys = Object.keys(this), res = []
    for (var i=0; i<keys.length; i++) {key = keys[i]; res.push([key, this[key]]);}
    return res;
}"""

METHODS['keys'] = """function () { // nargs: 0
    if (typeof this['KEY'] === 'function') return this.KEY.apply(this, arguments);
    return Object.keys(this);
}"""

METHODS['popitem'] = """function () { // nargs: 0
    if (this.constructor !== Object) return this.KEY.apply(this, arguments);
    var keys, key, val;
    keys = Object.keys(this);
    if (keys.length == 0) {var e = Error(); e.name='KeyError'; throw e;}
    key = keys[0]; val = this[key]; delete this[key];
    return [key, val];
}"""

METHODS['setdefault'] = """function (key, d) { // nargs: 1 2
    if (this.constructor !== Object) return this.KEY.apply(this, arguments);
    if (this[key] !== undefined) {return this[key];}
    else if (d !== undefined) { this[key] = d; return d;}
    else {return null;}
}"""

METHODS['update'] = """function (other) { // nargs: 1
    if (this.constructor !== Object) return this.KEY.apply(this, arguments);
    var key, keys = Object.keys(other);
    for (var i=0; i<keys.length; i++) {key = keys[i]; this[key] = other[key];}
}"""

METHODS['values'] = """function () { // nargs: 0
    if (this.constructor !== Object) return this.KEY.apply(this, arguments);
    var key, keys = Object.keys(this), res = [];
    for (var i=0; i<keys.length; i++) {key = keys[i]; res.push(this[key]);}
    return res;
}"""

## String only

# ignores: encode, decode, format, format_map, isdecimal, isdigit,
# isprintable, maketrans

METHODS['capitalize'] = """function () { // nargs: 0
    if (this.constructor !== String) return this.KEY.apply(this, arguments);
    return this.slice(0, 1).toUpperCase() + this.slice(1).toLowerCase();
}"""

METHODS['casefold'] = """function () { // nargs: 0
    if (this.constructor !== String) return this.KEY.apply(this, arguments);
    return this.toLowerCase();
}"""

METHODS['center'] = """function (w, fill) { // nargs: 1 2
    if (this.constructor !== String) return this.KEY.apply(this, arguments);
    fill = (fill === undefined) ? ' ' : fill;
    var tofill = Math.max(0, w - this.length);
    var left = Math.ceil(tofill / 2);
    var right = tofill - left;
    return fill.repeat(left) + this + fill.repeat(right);
}"""

METHODS['endswith'] = """function (x) { // nargs: 1
    if (this.constructor !== String) return this.KEY.apply(this, arguments);
    return this.lastIndexOf(x) == this.length - x.length;
}"""

METHODS['expandtabs'] = """function (tabsize) { // nargs: 0 1
    if (this.constructor !== String) return this.KEY.apply(this, arguments);
    tabsize = (tabsize === undefined) ? 8 : tabsize;
    return this.replace(/\\t/g, ' '.repeat(tabsize));
}"""

METHODS['find'] = """function (x, start, stop) { // nargs: 1 2 3
    if (this.constructor !== String) return this.KEY.apply(this, arguments);
    start = (start === undefined) ? 0 : start;
    stop = (stop === undefined) ? this.length : stop;
    start = Math.max(0, ((start < 0) ? this.length + start : start));
    stop = Math.min(this.length, ((stop < 0) ? this.length + stop : stop));
    var i = this.slice(start, stop).indexOf(x);
    if (i >= 0) return i + start;
    return -1;
}"""

METHODS['isalnum'] = """function () { // nargs: 0
    if (this.constructor !== String) return this.KEY.apply(this, arguments);
    return Boolean(/^[A-Za-z0-9]+$/.test(this));
}"""

METHODS['isalpha'] = """function () { // nargs: 0
    if (this.constructor !== String) return this.KEY.apply(this, arguments);
    return Boolean(/^[A-Za-z]+$/.test(this));
}"""

# METHODS['isdecimal'] = """function () {
#     if (this.constructor !== String) return this.KEY.apply(this, arguments);
#     return Boolean(/^[0-9]+$/.test(this));
# }"""
# 
# METHODS['isdigit'] = METHODS['isdecimal']

METHODS['isidentifier'] = """function () { // nargs: 0
    if (this.constructor !== String) return this.KEY.apply(this, arguments);
    return Boolean(/^[A-Za-z_][A-Za-z0-9_]*$/.test(this));
}"""

METHODS['islower'] = """function () { // nargs: 0
    if (this.constructor !== String) return this.KEY.apply(this, arguments);
    var low = this.toLowerCase(), high = this.toUpperCase();
    return low != high && low == this;
}"""

METHODS['isnumeric'] = """function () { // nargs: 0
    if (this.constructor !== String) return this.KEY.apply(this, arguments);
    return Boolean(/^[0-9]+$/.test(this));
}"""

METHODS['isspace'] = """function () { // nargs: 0
    if (this.constructor !== String) return this.KEY.apply(this, arguments);
    return Boolean(/^\\s+$/.test(this));
}"""

METHODS['istitle'] = """function () { // nargs: 0
    if (this.constructor !== String) return this.KEY.apply(this, arguments);
    var low = this.toLowerCase(), title = this.METHOD_PREFIXtitle();
    return low != title && title == this;
}"""

METHODS['isupper'] = """function () { // nargs: 0
    if (this.constructor !== String) return this.KEY.apply(this, arguments);
    var low = this.toLowerCase(), high = this.toUpperCase();
    return low != high && high == this;
}"""

METHODS['join'] = """function (x) { // nargs: 1
    if (this.constructor !== String) return this.KEY.apply(this, arguments);
    return x.join(this);  // call join on the list instead of the string.   
}"""

METHODS['ljust'] = """function (w, fill) { // nargs: 1 2
    if (this.constructor !== String) return this.KEY.apply(this, arguments);
    fill = (fill === undefined) ? ' ' : fill;
    var tofill = Math.max(0, w - this.length);
    return this + fill.repeat(tofill);
}"""

METHODS['lower'] = """function () { // nargs: 0
    if (this.constructor !== String) return this.KEY.apply(this, arguments);
    return this.toLowerCase();
}"""

METHODS['lstrip'] = """function (chars) { // nargs: 0 1
    if (this.constructor !== String) return this.KEY.apply(this, arguments);
    chars = (chars === undefined) ? ' \\t\\r\\n' : chars;
    for (var i=0; i<this.length; i++) {
        if (chars.indexOf(this[i]) < 0) return this.slice(i);
    } return '';
}"""

METHODS['partition'] = """function (sep) { // nargs: 1
    if (this.constructor !== String) return this.KEY.apply(this, arguments);
    if (sep === '') {var e = Error('empty sep'); e.name='ValueError'; throw e;}
    var i1 = this.indexOf(sep);
    if (i1 < 0) return [this.slice(0), '', '']
    var i2 = i1 + sep.length;
    return [this.slice(0, i1), this.slice(i1, i2), this.slice(i2)]; 
}"""

METHODS['replace'] = """function (s1, s2, count) {  // nargs: 2 3
    if (this.constructor !== String) return this.KEY.apply(this, arguments);
    var i = 0, i2, parts = [];
    count = (count === undefined) ? 1e20 : count;
    while (count > 0) {
        i2 = this.indexOf(s1, i);
        if (i2 >= 0) {
            parts.push(this.slice(i, i2));
            parts.push(s2);
            i = i2 + s1.length;
            count -= 1;
        } else break;
    }
    parts.push(this.slice(i));
    return parts.join('');
}"""

METHODS['rfind'] = """function (x, start, stop) { // nargs: 1 2 3
    if (this.constructor !== String) return this.KEY.apply(this, arguments);
    start = (start === undefined) ? 0 : start;
    stop = (stop === undefined) ? this.length : stop;
    start = Math.max(0, ((start < 0) ? this.length + start : start));
    stop = Math.min(this.length, ((stop < 0) ? this.length + stop : stop));
    var i = this.slice(start, stop).lastIndexOf(x);
    if (i >= 0) return i + start;
    return -1;
}"""

METHODS['rindex'] = """function (x, start, stop) {  // nargs: 1 2 3
    if (this.constructor !== String) return this.KEY.apply(this, arguments);
    var i = this.METHOD_PREFIXrfind(x, start, stop);
    if (i >= 0) return i;
    var e = Error(x); e.name='ValueError'; throw e;
}"""

METHODS['rjust'] = """function (w, fill) { // nargs: 1 2
    if (this.constructor !== String) return this.KEY.apply(this, arguments);
    fill = (fill === undefined) ? ' ' : fill;
    var tofill = Math.max(0, w - this.length);
    return fill.repeat(tofill) + this;
}"""

METHODS['rpartition'] = """function (sep) { // nargs: 1
    if (this.constructor !== String) return this.KEY.apply(this, arguments);
    if (sep === '') {var e = Error('empty sep'); e.name='ValueError'; throw e;}
    var i1 = this.lastIndexOf(sep);
    if (i1 < 0) return ['', '', this.slice(0)]
    var i2 = i1 + sep.length;
    return [this.slice(0, i1), this.slice(i1, i2), this.slice(i2)]; 
}"""

METHODS['rsplit'] = """function (sep, count) { // nargs: 1 2
    if (this.constructor !== String) return this.KEY.apply(this, arguments);
    sep = (sep === undefined) ? /\\s/ : sep;
    count = Math.max(0, (count === undefined) ? 1e20 : count);
    var parts = this.split(sep);
    var limit = Math.max(0, parts.length-count);
    var res = parts.slice(limit);
    if (count < parts.length) res.splice(0, 0, parts.slice(0, limit).join(sep));
    return res;
}"""

METHODS['rstrip'] = """function (chars) { // nargs: 0 1
    if (this.constructor !== String) return this.KEY.apply(this, arguments);
    chars = (chars === undefined) ? ' \\t\\r\\n' : chars;
    for (var i=this.length-1; i>=0; i--) {
        if (chars.indexOf(this[i]) < 0) return this.slice(0, i+1);
    } return '';
}"""

METHODS['split'] = """function (sep, count) { // nargs: 0, 1 2
    if (this.constructor !== String) return this.KEY.apply(this, arguments);
    if (sep === '') {var e = Error('empty sep'); e.name='ValueError'; throw e;}
    sep = (sep === undefined) ? /\\s/ : sep;
    count = Math.max(0, (count === undefined) ? 1e20 : count);
    var parts = this.split(sep);
    var limit = Math.max(0, count);
    var res = parts.slice(0, limit);
    if (count < parts.length) res.push(parts.slice(limit).join(sep));
    return res;
}"""

METHODS['splitlines'] = """function (keepends) { // nargs: 0 1
    if (this.constructor !== String) return this.KEY.apply(this, arguments);
    keepends = keepends ? 1 : 0
    var finder = /\\r\\n|\\r|\\n/g;
    var i = 0, i2, isrn, parts = [];
    while (finder.exec(this) !== null) {
        i2 = finder.lastIndex -1;
        isrn = i2 > 0 && this[i2-1] == '\\r' && this[i2] == '\\n';
        if (keepends) parts.push(this.slice(i, finder.lastIndex));
        else parts.push(this.slice(i, i2 - isrn));
        i = finder.lastIndex;
    }
    if (i < this.length) parts.push(this.slice(i));
    else if (!parts.length) parts.push('');
    return parts;
}"""

METHODS['startswith'] = """function (x) { // nargs: 1
    if (this.constructor !== String) return this.KEY.apply(this, arguments);
    return this.indexOf(x) == 0;
}"""

METHODS['strip'] = """function (chars) { // nargs: 0 1
    if (this.constructor !== String) return this.KEY.apply(this, arguments);
    chars = (chars === undefined) ? ' \\t\\r\\n' : chars;
    var i, s1 = this, s2 = '', s3 = '';
    for (i=0; i<s1.length; i++) {
        if (chars.indexOf(s1[i]) < 0) {s2 = s1.slice(i); break;}
    } for (i=s2.length-1; i>=0; i--) {
        if (chars.indexOf(s2[i]) < 0) {s3 = s2.slice(0, i+1); break;}
    } return s3;
}"""

METHODS['swapcase'] = """function () { // nargs: 0
    if (this.constructor !== String) return this.KEY.apply(this, arguments);
    var c, res = [];
    for (var i=0; i<this.length; i++) {
        c = this[i];
        if (c.toUpperCase() == c) res.push(c.toLowerCase());
        else res.push(c.toUpperCase());
    } return res.join('');
}"""

METHODS['title'] = """function () { // nargs: 0
    if (this.constructor !== String) return this.KEY.apply(this, arguments);
    var i0, res = [], tester = /^[^A-Za-z]?[A-Za-z]$/;
    for (var i=0; i<this.length; i++) {
        i0 = Math.max(0, i-1);
        if (tester.test(this.slice(i0, i+1))) res.push(this[i].toUpperCase());
        else res.push(this[i].toLowerCase());
    } return res.join('');
}"""

METHODS['translate'] = """function (table) { // nargs: 1
    if (this.constructor !== String) return this.KEY.apply(this, arguments);
    var c, res = [];
    for (var i=0; i<this.length; i++) {
        c = table[this[i]];
        if (c === undefined) res.push(this[i]);
        else if (c !== null) res.push(c);
    } return res.join('');
}"""

METHODS['upper'] = """function () { // nargs: 0
    if (this.constructor !== String) return this.KEY.apply(this, arguments);
    return this.toUpperCase();
}"""

METHODS['zfill'] = """function (width) { // nargs: 1
    if (this.constructor !== String) return this.KEY.apply(this, arguments);
    return this.METHOD_PREFIXrjust(width, '0');
}"""


for key in METHODS:
    METHODS[key] = METHODS[key].replace(
        'KEY', key).replace(
        'FUNCTION_PREFIX', FUNCTION_PREFIX).replace(
        'METHOD_PREFIX', METHOD_PREFIX)

for key in FUNCTIONS:
    FUNCTIONS[key] = FUNCTIONS[key].replace(
        'KEY', key).replace(
        'FUNCTION_PREFIX', FUNCTION_PREFIX).replace(
        'METHOD_PREFIX', METHOD_PREFIX)

## Modules - experimental

import sys
IMPORTS = {}
IMPORTS['sys'] = {}

IMPORTS['sys'] = None  # mark sys as a module
IMPORTS['sys.version_info'] = "[%s]" % ', '.join([str(x) for x in sys.version_info[:3]])
IMPORTS['sys.version'] = "%r" % ('.'.join([str(x) for x in sys.version_info[:3]])
                                    + ' [PyScript]')
IMPORTS['sys.path'] = "[]"

IMPORTS['time'] = None  # mark time as a module
IMPORTS['time.perf_counter'] = """function() {
    if (typeof(process) === "undefined"){return performance.now()*1e-3;}
    else {var t = process.hrtime(); return t[0] + t[1]*1e-9;}
}"""  # Work in nodejs and browser

IMPORTS['time.clock'] = IMPORTS['time.perf_counter']
IMPORTS['time.time'] = """function () {return new Date().getTime() / 1000;}"""

IMPORTS['time.sleep'] = """function(secs) {
    var msecs = secs * 1000, start = new Date();
    while (new Date() - start < msecs) {}
}""" 
