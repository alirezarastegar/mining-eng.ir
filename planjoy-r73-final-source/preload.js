'use strict';

const { contextBridge, ipcRenderer } = require('electron');

const invoke = (channel, ...args) => ipcRenderer.invoke(channel, ...args);
const subscribe = (channel, callback) => {
  if (typeof callback !== 'function') return () => {};
  const listener = (_event, payload) => callback(payload);
  ipcRenderer.on(channel, listener);
  return () => ipcRenderer.removeListener(channel, listener);
};

contextBridge.exposeInMainWorld('planjoy', Object.freeze({
  getState: () => invoke('state:get'),
  saveState: state => invoke('state:save', state),
  resetDemo: () => invoke('state:reset-demo'),
  platform: () => invoke('system:platform'),
  setStartup: enabled => invoke('system:startup', Boolean(enabled)),
  openExternal: url => invoke('system:open-external', String(url || '')),
  notify: (title, body) => invoke('notify:test', { title: String(title || 'PlanJoy'), body: String(body || '') }),
  openWidget: type => invoke('widget:open', String(type || 'today')),
  backup: () => invoke('data:backup'),
  restore: () => invoke('data:restore'),
  exportCsv: () => invoke('data:export-csv'),
  exportIcs: () => invoke('data:export-ics'),
  syncCreate: config => invoke('sync:create', config || {}),
  syncConfigure: config => invoke('sync:configure', config || {}),
  syncNow: () => invoke('sync:now'),
  syncRevoke: deviceId => invoke('sync:revoke', String(deviceId || '')),
  diagnostics: () => invoke('diagnostics:export'),
  checkUpdate: url => invoke('update:check', String(url || '')),
  onStateChanged: callback => subscribe('state:changed', callback),
  onOpenRoute: callback => subscribe('route:open', callback)
}));
