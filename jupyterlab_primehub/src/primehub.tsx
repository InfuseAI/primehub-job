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
        console.log('showSubmitJObDialog has not yet implemented');   
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