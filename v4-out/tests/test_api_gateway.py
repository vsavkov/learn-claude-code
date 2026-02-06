import pytest
from httpx import ASGITransport, AsyncClient

import api_gateway


@pytest.mark.anyio
async def test_health_ok():
    transport = ASGITransport(app=api_gateway.app)
    async with AsyncClient(transport=transport, base_url='http://test') as client:
        response = await client.get('/health')
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}


@pytest.mark.anyio
async def test_query_success_envelope(monkeypatch):
    def fake_run_agent_with_trace(user_message, model, max_tokens, timeout_seconds):
        return 'ok answer', [], []

    monkeypatch.setattr(api_gateway, 'run_agent_with_trace', fake_run_agent_with_trace)

    transport = ASGITransport(app=api_gateway.app)
    async with AsyncClient(transport=transport, base_url='http://test') as client:
        response = await client.post('/agent/query', json={'query': 'show labs'})

    assert response.status_code == 200
    data = response.json()
    assert data['answer'] == 'ok answer'
    assert isinstance(data['tool_calls'], list)
    assert isinstance(data['raw_outputs'], list)
    assert 'timing_ms' in data
    assert 'request_id' in data
    assert 'timestamp' in data


@pytest.mark.anyio
async def test_query_empty_validation_error():
    transport = ASGITransport(app=api_gateway.app)
    async with AsyncClient(transport=transport, base_url='http://test') as client:
        response = await client.post('/agent/query', json={'query': '   '})
    assert response.status_code == 422


@pytest.mark.anyio
async def test_query_gateway_error(monkeypatch):
    def fake_run_agent_with_trace(user_message, model, max_tokens, timeout_seconds):
        raise api_gateway.GatewayError(
            error_code='request_timeout',
            message='Request exceeded timeout',
            status_code=504,
        )

    monkeypatch.setattr(api_gateway, 'run_agent_with_trace', fake_run_agent_with_trace)

    transport = ASGITransport(app=api_gateway.app)
    async with AsyncClient(transport=transport, base_url='http://test') as client:
        response = await client.post('/agent/query', json={'query': 'show labs'})

    assert response.status_code == 504
    data = response.json()
    assert data['error_code'] == 'request_timeout'
    assert data['message'] == 'Request exceeded timeout'
    assert 'request_id' in data
