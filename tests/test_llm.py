from qa_agent.llm import AnthropicAdapter, GeminiAdapter, OpenAICompatibleAdapter


def test_openai_compatible_adapter_keeps_provider_config():
    adapter = OpenAICompatibleAdapter(
        api_key="secret",
        model="test-model",
        base_url="https://example.com/v1/",
        provider_name="openai",
    )
    assert adapter.model == "test-model"
    assert adapter.base_url == "https://example.com/v1"


def test_adapter_classes_exist():
    assert GeminiAdapter
    assert AnthropicAdapter
