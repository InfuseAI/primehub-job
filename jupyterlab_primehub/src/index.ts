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
  id: 'jupyterlab-primehub:job-submit-plugin',
  autoStart: true
};

export
class PrimeHubExtenstion implements DocumentRegistry.IWidgetExtension<NotebookPanel, INotebookModel> {
  createNew(panel: NotebookPanel, context: DocumentRegistry.IContext<INotebookModel>): IDisposable {
    let button = new PrimeHubDropdownList();
    panel.toolbar.insertAfter('cellType', 'primehubFunctions', button);
    return new DisposableDelegate(() => {
      button.dispose();
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