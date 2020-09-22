import {
  IDisposable, DisposableDelegate
} from '@lumino/disposable';

import {
  JupyterFrontEnd, JupyterFrontEndPlugin
} from '@jupyterlab/application';

import {
  DocumentRegistry
} from '@jupyterlab/docregistry';

import {
  NotebookPanel, INotebookModel
} from '@jupyterlab/notebook';

import {
  PrimeHubDropdownList
} from './primehub'

const plugin: JupyterFrontEndPlugin<void> = {
  activate,
  id: 'jupyterlab-primehub',
  autoStart: true
};

export
class PrimeHubExtenstion implements DocumentRegistry.IWidgetExtension<NotebookPanel, INotebookModel> {
  createNew(panel: NotebookPanel, context: DocumentRegistry.IContext<INotebookModel>): IDisposable {
    const widget = new PrimeHubDropdownList(panel);
    panel.toolbar.insertAfter('cellType', 'primehubFunctions', widget);
    return new DisposableDelegate(() => {
      widget.dispose();
    });
  }
}

/**
 * Activate the extension.
 */
function activate(app: JupyterFrontEnd) {
  app.docRegistry.addWidgetExtension('Notebook', new PrimeHubExtenstion());
};

/**
 * Export the plugin as default.
 */
export default plugin;