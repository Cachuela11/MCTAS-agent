def create_model(model_id: str, api_key: str = ""):
    from agno.models.deepseek import DeepSeek
    kwargs = {"id": model_id}
    if api_key:
        kwargs["api_key"] = api_key
    return DeepSeek(**kwargs)
