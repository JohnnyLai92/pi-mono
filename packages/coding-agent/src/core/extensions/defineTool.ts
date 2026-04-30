/**
 * Legacy compat stub for `defineTool`.
 *
 * Some extensions reference `defineTool` expecting the old API.
 * This module provides a no-op version so the loader does not crash with
 * "is not a function".
 *
 * Old signature: defineTool(name, description, execute)
 * New API: registerTool(ToolDefinition)
 *
 * @module @mariozechner/pi-coding-agent/defineTool
 */

/**
 * @deprecated Use `registerTool` on the extension context instead.
 */
export function defineTool(
	name: string,
	description: string,
	execute: (...args: unknown[]) => unknown,
	// eslint-disable-next-line @typescript-eslint/no-unused-vars
): void {
	// no-op — extensions should migrate to the new tool registration API
	// via `context.registerTool({ name, description, execute })` on the
	// extension context object.
}


