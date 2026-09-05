/**
 * Obsidian Property Studio v1.2.0
 * StateTransfer — Client-side Explicit Cross-Module Navigation & Context Transfer Engine
 * 
 * Implements REQ-040 & DEC-031:
 * - Guarantees zero dead-end CTAs
 * - Transmits context explicitly (schema_id, finding_id, note_path, proposal_data)
 * - Single-use consumption prevents stale intent replay
 */

(function(root) {
  'use strict';

  class StateTransferManager {
    constructor() {
      this._pending = new Map();
      this._listeners = new Set();
      this._history = [];
    }

    /**
     * Sets a pending navigation payload for a target module.
     * @param {string} targetModule - Target module name (e.g. 'workspace', 'design', 'health')
     * @param {Object} payload - Navigation context payload
     * @param {string} [intent='navigate'] - Navigation intent (e.g. 'reconcile', 'inspect_finding', 'edit_candidate')
     */
    setPending(targetModule, payload = {}, intent = 'navigate') {
      if (!targetModule || typeof targetModule !== 'string') {
        console.error('[StateTransfer] Invalid targetModule:', targetModule);
        return;
      }
      const context = {
        targetModule: targetModule.trim(),
        intent: intent,
        timestamp: Date.now(),
        ...payload
      };
      this._pending.set(targetModule.trim(), context);
      this._history.push({ ...context });
      if (this._history.length > 50) this._history.shift();
      this._notify(targetModule.trim(), context);
    }

    /**
     * Checks whether a pending navigation context exists for the target module.
     * @param {string} targetModule
     * @returns {boolean}
     */
    hasPending(targetModule) {
      return this._pending.has(targetModule);
    }

    /**
     * Inspects the pending context without consuming it.
     * @param {string} targetModule
     * @returns {Object|null}
     */
    peekPending(targetModule) {
      return this._pending.get(targetModule) || null;
    }

    /**
     * Retrieves and clears the pending context for the target module (single-use consumption).
     * @param {string} targetModule
     * @returns {Object|null}
     */
    consumePending(targetModule) {
      const ctx = this._pending.get(targetModule);
      if (ctx) {
        this._pending.delete(targetModule);
        return ctx;
      }
      return null;
    }

    /**
     * Clears all pending contexts.
     */
    clearAll() {
      this._pending.clear();
    }

    /**
     * Subscribe to state transfer events.
     * @param {Function} listener
     */
    subscribe(listener) {
      if (typeof listener === 'function') {
        this._listeners.add(listener);
      }
      return () => this._listeners.delete(listener);
    }

    _notify(moduleName, context) {
      for (const listener of this._listeners) {
        try {
          listener(moduleName, context);
        } catch (e) {
          console.error('[StateTransfer] Listener error:', e);
        }
      }
    }
  }

  const instance = new StateTransferManager();

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = { StateTransfer: instance, StateTransferManager };
  } else {
    root.StateTransfer = instance;
    root.StateTransferManager = StateTransferManager;
  }
})(typeof window !== 'undefined' ? window : globalThis);
