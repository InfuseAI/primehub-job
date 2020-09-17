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

import { requestAPI } from './jupyterlab-primehub'; 

const plugin: JupyterFrontEndPlugin<void> = {
  activate,
  id: 'jupyterlab-primehub',
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
  getValueFromServer();
};

function getValueFromServer() {
  requestAPI<any>('get_example')
  .then(data => {
    console.log('serverextension example');
    console.log(data);
  })
  .catch(reason => {
    console.error(
      `The jupyterlab_primehub server extension appears to be missing.\n${reason}`
    );
  });
}

/**
 * Export the plugin as default.
 */
export default plugin;