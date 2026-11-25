/**
 * Zero-dependency Model Context Protocol (MCP) JSON-RPC 2.0 stdio server for Algerian Darja NLP.
 */
import * as readline from 'readline';
import { executeAgentTool, getMcpToolDefinitions } from './agent';

export function handleMcpMessage(msg: Record<string, any>): Record<string, any> | null {
  const reqId = msg?.id;
  const method = String(msg?.method || '');
  const params = msg?.params || {};

  if (reqId === undefined && method.startsWith('notifications/')) {
    return null;
  }

  let result: Record<string, any>;
  if (method === 'initialize') {
    result = {
      protocolVersion: '2024-11-05',
      capabilities: { tools: {} },
      serverInfo: { name: 'darja-nlp-kit', version: '2.0.0' },
    };
  } else if (method === 'ping') {
    result = {};
  } else if (method === 'tools/list') {
    result = { tools: getMcpToolDefinitions() };
  } else if (method === 'tools/call') {
    const toolName = String(params.name || '');
    const args = params.arguments || {};
    const toolOut = executeAgentTool(toolName, args);
    const isErr = Boolean(toolOut && typeof toolOut === 'object' && 'error' in toolOut && Object.keys(toolOut).length === 1);
    result = {
      content: [{ type: 'text', text: JSON.stringify(toolOut) }],
      isError: isErr,
    };
  } else {
    if (reqId === undefined || reqId === null) return null;
    return {
      jsonrpc: '2.0',
      id: reqId,
      error: { code: -32601, message: `Method not found: ${method}` },
    };
  }

  if (reqId === undefined) return null;
  return { jsonrpc: '2.0', id: reqId, result };
}

export function runMcpServer(): void {
  process.stderr.write('[darja-nlp-kit] MCP server ready on stdio (zero-dependency).\n');
  const rl = readline.createInterface({ input: process.stdin, crlfDelay: Infinity });
  rl.on('line', (line) => {
    const raw = line.trim();
    if (!raw) return;
    try {
      const msg = JSON.parse(raw);
      const resp = handleMcpMessage(msg);
      if (resp !== null) {
        process.stdout.write(JSON.stringify(resp) + '\n');
      }
    } catch (err: any) {
      process.stdout.write(
        JSON.stringify({
          jsonrpc: '2.0',
          id: null,
          error: { code: -32700, message: `Parse error: ${err?.message || err}` },
        }) + '\n'
      );
    }
  });
}
