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

import { IMainMenu } from '@jupyterlab/mainmenu';
import { JobStatusWidget } from './sidebar';

const plugin: JupyterFrontEndPlugin<void> = {
  activate,
  id: 'jupyterlab-primehub',
  optional: [IMainMenu],
  autoStart: true
};

import { LabIcon } from '@jupyterlab/ui-components';
import jobs from '../style/jobs.svg';

export const jobsIcon = new LabIcon({ name: 'primehub-jobs', svgstr: jobs });

const jobStatusWidget = new JobStatusWidget();
jobStatusWidget.id = 'jupyterlab-primehub:job-status';
jobStatusWidget.title.icon = jobsIcon;
jobStatusWidget.title.caption = 'Jobs';

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
function activate(
  app: JupyterFrontEnd, 
  mainMenu: IMainMenu | null) {
  app.docRegistry.addWidgetExtension('Notebook', new PrimeHubExtenstion());
  console.log(mainMenu);

  // Add job-status sidebar
  app.shell.add(jobStatusWidget, 'left');
};

/**
 * Export the plugin as default.
 */
export default plugin;