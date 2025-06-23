import * as assert from 'assert';
import * as vscode from 'vscode';
import * as sinon from 'sinon';
import { afterEach } from 'mocha';
import { ApiClient } from '../../api/api-client';
import { WorkflowManager } from '../../api/workflow-manager';

suite('Extension Test Suite', () => {
	
  afterEach(() => {
    sinon.restore();
  });

  test('Extension should be present', () => {
    assert.ok(vscode.extensions.getExtension('project-s.vscode-extension'));
  });

  test('Should register commands', async () => {
    const commands = await vscode.commands.getCommands();
    
    // Check that our commands are registered
    assert.ok(commands.includes('project-s.connect'));
    assert.ok(commands.includes('project-s.analyze'));
    assert.ok(commands.includes('project-s.generate'));
    assert.ok(commands.includes('project-s.document'));
    assert.ok(commands.includes('project-s.createWorkflow'));
  });

  test('ApiClient connect should update status', async () => {
    const extension = vscode.extensions.getExtension('project-s.vscode-extension');
    if (!extension) {
      assert.fail('Extension not found');
    }
    
    const apiClient = extension.exports.apiClient as ApiClient;
    
    // Create a spy for the emit method
    const emitSpy = sinon.spy(apiClient, 'emit');
    
    // Mock the connect method
    const connectStub = sinon.stub(apiClient, 'connect').resolves(true);
    
    // Call connect
    await apiClient.connect();
    
    // Verify connect was called
    assert.ok(connectStub.called);
    
    // Check that the 'connect' event was emitted
    assert.ok(emitSpy.calledWith('connect'));
  });

  test('WorkflowManager should list workflows', async () => {
    const extension = vscode.extensions.getExtension('project-s.vscode-extension');
    if (!extension) {
      assert.fail('Extension not found');
    }
    
    const workflowManager = extension.exports.workflowManager as WorkflowManager;
    const apiClient = extension.exports.apiClient as ApiClient;
    
    // Mock the API response
    const mockWorkflows = [
      { id: '1', name: 'Test Workflow 1', type: 'test' },
      { id: '2', name: 'Test Workflow 2', type: 'test' }
    ];
    
    // Stub the sendRequest method
    const sendRequestStub = sinon.stub(apiClient, 'sendRequest').resolves({
      success: true,
      data: mockWorkflows
    });
    
    // Call listWorkflows
    const workflows = await workflowManager.listWorkflows();
    
    // Verify the request was made
    assert.ok(sendRequestStub.calledWith('GET', '/workflows'));
    
    // Check the returned workflows
    assert.deepStrictEqual(workflows, mockWorkflows);
  });
});
