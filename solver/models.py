def create_model(model_id: str, api_key: str = ""):
    from agno.models.google import Gemini
    kwargs = {"id": model_id}
    if api_key:
        kwargs["api_key"] = api_key
    return Gemini(**kwargs)
