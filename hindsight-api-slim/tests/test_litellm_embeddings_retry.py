"""Tests for LiteLLM embeddings retry mechanism, error recovery, and dimensions configuration."""

from unittest.mock import patch

import httpx
import pytest

from hindsight_api.config import (
    ENV_EMBEDDINGS_LITELLM_DIMENSIONS,
    ENV_EMBEDDINGS_PROVIDER,
    clear_config_cache,
)
from hindsight_api.engine.embeddings import (
    EmbeddingRetryPolicy,
    LiteLLMEmbeddings,
    create_embeddings_from_env,
)


@pytest.mark.asyncio
async def test_litellm_embeddings_dimension_override_skips_probe() -> None:
    """When dimensions is configured, initialize() must skip the network probe entirely."""
    embeddings = LiteLLMEmbeddings(
        api_base="http://test-litellm:4000",
        model="custom-model",
        dimensions=768,
    )

    with patch.object(httpx.Client, "post") as mock_post:
        await embeddings.initialize()
        mock_post.assert_not_called()

    assert embeddings.dimension == 768


@pytest.mark.asyncio
async def test_litellm_embeddings_initialize_probe_success() -> None:
    """When dimensions is not set, initialize() probes the endpoint and detects vector dimension."""
    embeddings = LiteLLMEmbeddings(
        api_base="http://test-litellm:4000",
        model="text-embedding-3-small",
        retry_policy=EmbeddingRetryPolicy(initial_backoff=0.01),
    )

    mock_resp = httpx.Response(
        200,
        json={"data": [{"embedding": [0.1] * 1024, "index": 0}]},
        request=httpx.Request("POST", "http://test-litellm:4000/embeddings"),
    )

    with patch.object(httpx.Client, "post", return_value=mock_resp) as mock_post:
        await embeddings.initialize()
        mock_post.assert_called_once()

    assert embeddings.dimension == 1024


@pytest.mark.asyncio
async def test_litellm_embeddings_probe_retries_on_500_and_recovers() -> None:
    """Probe should retry on transient 500 errors and succeed once proxy is ready."""
    embeddings = LiteLLMEmbeddings(
        api_base="http://test-litellm:4000",
        model="text-embedding-3-small",
        retry_policy=EmbeddingRetryPolicy(max_retries=3, initial_backoff=0.01),
    )

    req = httpx.Request("POST", "http://test-litellm:4000/embeddings")
    err_resp = httpx.Response(500, request=req)
    ok_resp = httpx.Response(
        200,
        json={"data": [{"embedding": [0.1] * 1536, "index": 0}]},
        request=req,
    )

    with patch.object(httpx.Client, "post", side_effect=[err_resp, err_resp, ok_resp]) as mock_post:
        await embeddings.initialize()
        assert mock_post.call_count == 3

    assert embeddings.dimension == 1536


@pytest.mark.asyncio
async def test_litellm_embeddings_probe_retries_on_connect_error_and_recovers() -> None:
    """Probe should retry on connection error (e.g. proxy starting up) and succeed."""
    embeddings = LiteLLMEmbeddings(
        api_base="http://test-litellm:4000",
        model="text-embedding-3-small",
        retry_policy=EmbeddingRetryPolicy(max_retries=3, initial_backoff=0.01),
    )

    req = httpx.Request("POST", "http://test-litellm:4000/embeddings")
    ok_resp = httpx.Response(
        200,
        json={"data": [{"embedding": [0.1] * 1536, "index": 0}]},
        request=req,
    )

    with patch.object(
        httpx.Client,
        "post",
        side_effect=[httpx.ConnectError("Connection refused", request=req), ok_resp],
    ) as mock_post:
        await embeddings.initialize()
        assert mock_post.call_count == 2

    assert embeddings.dimension == 1536


@pytest.mark.asyncio
async def test_litellm_embeddings_probe_exhausts_retries_and_raises() -> None:
    """Probe should raise RuntimeError after exhausting max_retries."""
    embeddings = LiteLLMEmbeddings(
        api_base="http://test-litellm:4000",
        model="text-embedding-3-small",
        retry_policy=EmbeddingRetryPolicy(max_retries=2, initial_backoff=0.01),
    )

    req = httpx.Request("POST", "http://test-litellm:4000/embeddings")
    err_resp = httpx.Response(500, request=req)

    with patch.object(httpx.Client, "post", side_effect=[err_resp, err_resp, err_resp]) as mock_post:
        with pytest.raises(RuntimeError, match="Failed to connect to LiteLLM proxy"):
            await embeddings.initialize()
        assert mock_post.call_count == 3


def test_litellm_embeddings_encode_retries_on_503_and_succeeds() -> None:
    """encode() should retry transient 503 errors and recover."""
    embeddings = LiteLLMEmbeddings(
        api_base="http://test-litellm:4000",
        model="text-embedding-3-small",
        dimensions=512,
        retry_policy=EmbeddingRetryPolicy(max_retries=2, initial_backoff=0.01),
    )

    # Initialize client with dimensions override (0 probe calls)
    embeddings._client = httpx.Client()
    embeddings._dimension = 512

    req = httpx.Request("POST", "http://test-litellm:4000/embeddings")
    err_resp = httpx.Response(503, request=req)
    ok_resp = httpx.Response(
        200,
        json={
            "data": [
                {"embedding": [0.1] * 512, "index": 0},
                {"embedding": [0.2] * 512, "index": 1},
            ]
        },
        request=req,
    )

    with patch.object(httpx.Client, "post", side_effect=[err_resp, ok_resp]) as mock_post:
        res = embeddings.encode(["hello", "world"])
        assert len(res) == 2
        assert len(res[0]) == 512
        assert mock_post.call_count == 2
        # Check payload included dimensions
        call_kwargs = mock_post.call_args[1]
        assert call_kwargs["json"]["dimensions"] == 512


def test_create_embeddings_from_env_with_dimensions(monkeypatch: pytest.MonkeyPatch) -> None:
    """create_embeddings_from_env() should parse HINDSIGHT_API_EMBEDDINGS_LITELLM_DIMENSIONS."""
    monkeypatch.setenv(ENV_EMBEDDINGS_PROVIDER, "litellm")
    monkeypatch.setenv(ENV_EMBEDDINGS_LITELLM_DIMENSIONS, "384")

    clear_config_cache()
    try:
        embeddings = create_embeddings_from_env()
        assert isinstance(embeddings, LiteLLMEmbeddings)
        assert embeddings.dimensions == 384
    finally:
        clear_config_cache()
