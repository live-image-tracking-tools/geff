# Adding a new backend

## Read from a new backend

Follow these steps to add read support for a new graph backend.

1. Add your backend to the [`SupportedBackend`](_api_wrapper.py#L19) `Literal` type at the start of the `_graph_libs/_api_wrapper.py` file.

2. Create a module for functions related to your backend, the required functions are defined in the [`Backend`](_backend_protocol.py#L12) class.

> [!NOTE]
> `Backend` is a Python `Protocol`. A python `Protocol` is a way to do structural type hinting, in our case it means a static type checker, such as `mypy`, will enforce anything typed as `Backend` must have a `GRAPH_TYPES` attribute and the functions `construct`, `get_node_ids`, `get_edge_ids`, `get_node_prop` and `get_edge_prop`. Module instances can also be typed as a protocol.

3. Add a case to the `match-case` block in the [`get_backend`](_api_wrapper.py#38) function. You should also add an overload for this function, following the other backends as an example.

> [!NOTE]
> `Backend` is defined in a way that means you can use the syntax `Backend[GraphType]` so that a static type checker will know, for example, that the `construct` function in the backend will return an object with the type `GraphType`. This is how you should overload the return of `get_backend` for your case.

> [!TIP]
> Unfortunately mypy will not give an informative error here if you have not created your module correctly. However if you are also using Pylance, which uses Pyright under the hood, it will tell you:
> ```console
> Type "Module("geff._graph_libs._dummy_backend")" is not assignable to return type "Backend[Unknown]"
>  "GRAPH_TYPES" is not present
>  "construct" is not present
>  "get_node_ids" is not present
>  "get_edge_ids" is not present
>  "get_node_prop" is not present
>  "get_edge_prop" is not present
>  ```
> where `_dummy_backend.py` is an empty module added to `_graph_libs`.

4. Additionally overload the [`read`](_api_wrapper.py#L98) function, following the other backends as an example. The backend argument should be typed as `Literal[<your-backend-string>]` and if you can accept any additional arguments they should come after.

5. Your new backend will be tested automatically!

