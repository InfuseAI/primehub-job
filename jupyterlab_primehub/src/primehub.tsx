import {
    ReactWidget
} from '@jupyterlab/apputils';

import {
    HTMLSelect
} from '@jupyterlab/ui-components';

import { Widget } from '@lumino/widgets';

import React from 'react';

import { Dialog, showDialog } from '@jupyterlab/apputils';

export class PrimeHubDropdownList extends ReactWidget {

    constructor() {
        super();
    }

    handleChange = (event: React.ChangeEvent<HTMLSelectElement>): void => {
        if (event.target.value === "-") {
            return;
        }

        if (event.target.value === "submit-job") {
            this.showSubmitJObDialog();
        }

        if (event.target.value === "update-api-token") {
            this.showUpdateApiTokenDialog();
        }
    };

    showSubmitJObDialog = (): void => {
        showDialog({
            title: 'Submit Notebook as Job',
            body: new JobInfoInput(),
            buttons: [Dialog.cancelButton(), Dialog.okButton({label: 'Submit'})]
        }).then((result) => {
            console.log(result);
            if (result.button.label === "Cancel")
                return;
            //if (result.value.jobName.length === 0)
            //    console.log('empty job name');
            if (result.button.accept)
                this.submitNotebook(result.value);
        });
    }

    showUpdateApiTokenDialog = (): void => {
        showDialog({
            title: 'API Token',
            body: new ApiTokenInput(this.getApiToken()),
            buttons: [Dialog.cancelButton(), Dialog.okButton()]
        }).then((result) => {
            if (result.button.accept) {
                this.updateApiToken(result.value);
            }
        });
    }
    
    submitNotebook = (value: any): void => {
        console.log('submitNotebook has not been implemented yet');
        // submit job here
        showDialog({
            title: value.jobName.length > 0 ? 'Success' : 'Failed',
            body: new SubmitJobResult(value.jobName.toString()),
            buttons: [Dialog.okButton()]
        }).then((result) => {});
    }

    updateApiToken = (token: string): void => {
        localStorage.setItem('PrimeHub::API_TOKEN', token || "");
    }

    getApiToken = (): string => {
        return localStorage.getItem('PrimeHub::API_TOKEN') || "";
    }

    render() {
        let value = '-';
        return (
            <HTMLSelect
                onChange={this.handleChange}
                value={value}
            >
                <option value="-">PrimeHub</option>
                <option value="submit-job">Submit Notebook as Job</option>
                <option value="update-api-token">API Token</option>
            </HTMLSelect>
        );
    }
}

export interface IApiToken {
    value: string;
}

export class ApiTokenInput extends Widget {
    constructor(apiToken: string) {
        super();

        this._input = document.createElement('input', {});
        this._input.classList.add('jp-mod-styled');
        this._input.type = 'text';
        this._input.value = apiToken;

        // Initialize the node
        // this.node.appendChild(div);
        this.node.appendChild(this._input);
    }

    getValue(): string {
        return this._input.value;
    }

    protected _input: HTMLInputElement;
}

export class JobInfoInput extends Widget {
    constructor() {
        super();

        this.itLabel = document.createElement('label');
        this.itLabel.innerHTML = '* Instance Type';
        this.itLabel.style.marginTop = "20px";
        
        this.itSelector = document.createElement('select');
        let opt;
        for (let i = 0; i < 3; i++) {
            opt = document.createElement('option');
            opt.setAttribute('value', i.toString());
            opt.innerHTML = `it-${i}`;
            this.itSelector.appendChild(opt);
        }
        
        this.nameLabel = document.createElement('label');
        this.nameLabel.innerHTML = '* Job Name';
        this.nameLabel.style.marginTop = "20px";
        
        this.nameInput = document.createElement('input', {});
        //this.nameInput.classList.add('jp-mod-styled');
        this.nameInput.type = 'text';
        
        this.npLabel = document.createElement('label');
        this.npLabel.innerHTML = 'Notebook Parameters';
        this.npLabel.style.marginTop = "24px";
        
        this.npTextArea = document.createElement('textarea');
        /*
        this.groupResourceTable = document.createElement('table');
        let tr, th;
        for (let i = 0; i < 4; i++) {
            tr = document.createElement('tr');
            for (let j = 0; j < 3; j++) {
                th = document.createElement('th');
                th.innerHTML = `(${j})`;
                tr.appendChild(th);
            }
            this.groupResourceTable.appendChild(tr);
        }
        */
        
        this.node.appendChild(this.itLabel);
        this.node.appendChild(this.itSelector);
        this.node.appendChild(this.nameLabel);
        this.node.appendChild(this.nameInput);
        this.node.appendChild(this.npLabel);
        this.node.appendChild(this.npTextArea);
        //this.node.appendChild(this.groupResourceTable);
    }

    getValue(): any {
        //let ret = this.itSelector.value + ", " + this.nameInput.value + ", " + this.npTextArea.value;
        const values: { [key: string]: string; } = {};
        values["instanceType"] = this.itSelector.value.toString();
        values["jobName"] = this.nameInput.value.trim();
        values["notebookParameters"] = this.npTextArea.value.toString();

        return values;
    }
    
    protected itLabel: HTMLLabelElement;
    protected itSelector: HTMLSelectElement;
    protected nameLabel: HTMLLabelElement;
    protected nameInput: HTMLInputElement;
    protected npLabel: HTMLLabelElement;
    protected npTextArea: HTMLTextAreaElement;
    //protected groupResourceTable: HTMLTableElement;
}

export class SubmitJobResult extends Widget {
    constructor(jobName: string) {
        super();
        this.infoLabel = document.createElement('label');
        this.infoLabel.innerHTML = jobName.length > 0 ? `jobName: ${jobName}` : 'The job name is empty';
        this.node.appendChild(this.infoLabel);
    }
    protected infoLabel: HTMLLabelElement;
}
