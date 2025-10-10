def greet(name: str) -> str:
    return f"Hello, {name}!"

def dataframe_head_example():
    # Heavy deps imported lazily so importing the module stays light
    import pandas as pd
    return pd.DataFrame({"a":[1,2,3]}).head(2)
