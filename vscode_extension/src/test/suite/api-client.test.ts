import * as assert from 'assert';
import * as sinon from 'sinon';
import { afterEach } from 'mocha';
import { ApiClient } from '../../api/api-client';
import { TokenManager } from '../../utils/token-manager';
import { EventEmitter } from 'events';

suite('API Client Tests', () => {
  let apiClient: ApiClient;
  let tokenManagerStub: sinon.SinonStubbedInstance<TokenManager>;
  
  setup(() => {
    // Create a stub for the TokenManager
    tokenManagerStub = sinon.createStubInstance(TokenManager);
    apiClient = new ApiClient('http://localhost:8000', tokenManagerStub as unknown as TokenManager);
  });
  
  afterEach(() => {
    sinon.restore();
  });

  test('Should initialize with correct server URL', () => {
    assert.strictEqual(apiClient.serverUrl, 'http://localhost:8000');
  });

  test('Should connect successfully with valid token', async () => {
    // Stub getToken to return a valid token
    tokenManagerStub.getToken.returns('valid-token');
    
    // Stub fetch to return a successful response
    const fetchStub = sinon.stub(global, 'fetch').resolves({
      ok: true,
      status: 200,
      json: async () => ({ success: true })
    } as Response);
    
    // Mock EventEmitter's emit method to check it's called correctly
    const emitSpy = sinon.spy(EventEmitter.prototype, 'emit');
    
    // Call connect
    const result = await apiClient.connect();
    
    // Verify the result is true
    assert.strictEqual(result, true);
    
    // Verify fetch was called with the correct URL and headers
    assert.ok(fetchStub.calledWith('http://localhost:8000/api/status', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer valid-token'
      }
    }));
    
    // Verify the 'connect' event was emitted
    assert.ok(emitSpy.calledWith('connect'));
  });

  test('Should fail to connect with invalid token', async () => {
    // Stub getToken to return a valid token
    tokenManagerStub.getToken.returns('invalid-token');
    
    // Stub fetch to return an error response
    const fetchStub = sinon.stub(global, 'fetch').resolves({
      ok: false,
      status: 401,
      json: async () => ({ success: false, error: 'Unauthorized' })
    } as Response);
    
    // Mock EventEmitter's emit method to check it's called correctly
    const emitSpy = sinon.spy(EventEmitter.prototype, 'emit');
    
    // Call connect
    const result = await apiClient.connect();
    
    // Verify the result is false
    assert.strictEqual(result, false);
    
    // Verify the 'disconnect' event was emitted
    assert.ok(emitSpy.calledWith('disconnect'));
  });
  
  test('Should send request with correct parameters', async () => {
    // Stub getToken to return a valid token
    tokenManagerStub.getToken.returns('valid-token');
    
    // Stub fetch to return a successful response
    const fetchStub = sinon.stub(global, 'fetch').resolves({
      ok: true,
      status: 200,
      json: async () => ({ success: true, data: { test: 'data' } })
    } as Response);
    
    // Call sendRequest
    const result = await apiClient.sendRequest('POST', '/test-endpoint', { key: 'value' });
    
    // Verify fetch was called with the correct URL, method and body
    assert.ok(fetchStub.calledWith('http://localhost:8000/api/test-endpoint', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer valid-token'
      },
      body: JSON.stringify({ key: 'value' })
    }));
    
    // Verify the response was returned correctly
    assert.deepStrictEqual(result, { success: true, data: { test: 'data' } });
  });
  
  test('Should handle fetch errors gracefully', async () => {
    // Stub getToken to return a valid token
    tokenManagerStub.getToken.returns('valid-token');
    
    // Stub fetch to throw an error
    const fetchStub = sinon.stub(global, 'fetch').rejects(new Error('Network error'));
    
    try {
      // Call sendRequest
      await apiClient.sendRequest('GET', '/test-endpoint');
      assert.fail('Should have thrown an error');
    } catch (error) {
      // Verify that the error was caught and rethrown
      assert.ok(error instanceof Error);
      assert.strictEqual((error as Error).message, 'Network error');
    }
  });
});
