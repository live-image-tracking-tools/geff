# io module

## Read from a new backend

Follow these steps to add read support for a new graph backend.

1. Add your backend to the [`SupportedBackend`](supported_backends.py#L4) enum class.

2. Write a function that constructs your graph object from a set of NumPy arrays containing the GEFF data. Your construct function must follow the [`ConstructFunc`](read.py#L21) protocol.

> [!TIP]
> A python `Protocol` is a way to do structural type hinting, in our case it means a static type checker, such as `mypy`, will enforce anything typed as a `ConstructFunc` to have a matching function signature, i.e. it must have the arguments `metadata`, `node_ids`, `edge_ids`, `node_props` and `edge_props`; additional `args` and `kwargs` are allowed and the return type can be anything.

3. Add a case to the function [`get_construct_func`](read.py#L65) so that when your backend flag, which you added to `SupportedBackend`, is chosen, the new construct function you defined will be returned.

4. i. Add new overloads for the `get_construct_func` and [`read`](read.py#L107) functions, check the `networkx` overloads to see how it should be done. 
    
    ii. In the `read` implementation you will also need to add your backend to the `Literal` type for the `backend` argument.

> [!TIP]
> - For the `get_construct_func` function this should be:
>   ```python
>    @overload
>    def get_construct_func(
>        backend: Literal[SupportedBackend.YOUR_NEW_BACKEND],
>    ) -> ConstructFunc[<your graph type>]: ...
>   ```
> - For the `read` function this should be:
>   ```python
>    @overload
>    def read(
>        path: Path | str,
>        validate: bool,
>        node_props: list[str] | None,
>        edge_props: list[str] | None,
>        backend: Literal[SupportedBackend.YOUR_NEW_BACKEND],
>        backend_kwargs: dict[str, Any] | None = None,
>    ) -> tuple[<your graph type>, GeffMetadata]: ...
>   ```

5. Your new backend will be tested automatically, you will need to modify some utility functions to get the tests to pass:

    Add a case for your backend to the test utility functions, that are located above the `test_read` function, these are `is_expected_type`, `get_nodes`, `get_edges`, `get_node_prop` and `get_edge_prop`.

