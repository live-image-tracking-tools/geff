# Adding a new backend

## Read from a new backend

Follow these steps to add read support for a new graph backend.

1. Add your backend to the [`SupportedBackend`](_api_wrapper.py#L24) `Literal` type at the start of the `_graph_libs/_api_wrapper.py` file.

2. Create a concrete implementation of the [`Backend`](_backend_protocol.py#L16) class, you can subclass the `Backend` class to automatically have the `read` method after implementing the `construct` method. Have a look at the [`NxBackend`](_networkx.py#L84) as an example.

> [!NOTE]
> You will also have to create a concrete implementation of the [`GraphAdapter`](_graph_adapter.py#L11) class and have an instance of it be returned from the [`Backend.graph_adapter`](_backend_protocol.py#L137) method.

3. Add a case to the `match-case` block in the [`get_backend`](_api_wrapper.py#38) function. You should also add an overload for this function, following the other backends as an example.

> [!NOTE]
> `Backend` is defined in a way that means you can use the syntax `Backend[GraphType]` so that a static type checker will know, for example, that the `construct` function in the backend will return an object with the type `GraphType`. This is how you should overload the return of `get_backend` for your case.

4. 
    i. Additionally overload the [`read`](_api_wrapper.py#L98) function, following the other backends as an example. The backend argument should be typed as `Literal[<your-backend-string>]` and if you can accept any additional arguments they should come after.
    
    ii. If your write function has additional `args` and `kwargs` you should also write an overload for the write function so that users know what arguments are available for each graph type.

5. Your new backend will be tested automatically!

