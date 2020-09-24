import {
    ReactWidget
} from '@jupyterlab/apputils';

import {
    HTMLSelect
} from '@jupyterlab/ui-components';

import { Widget } from '@lumino/widgets';

import React from 'react';

import { Dialog, showDialog } from '@jupyterlab/apputils';
import { requestAPI } from './jupyterlab-primehub';
import { NotebookPanel } from '@jupyterlab/notebook';
import { StringInputComponent } from './components';

export class PrimeHubDropdownList extends ReactWidget {

    private panel: NotebookPanel;

    constructor(panel: NotebookPanel) {
        super();
        this.panel = panel;
    }

    getNodebookPath = (): string => {
        return this.panel.context.path;
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

        requestAPI<any>('resources', 'POST', 
            {
                'api_token': this.getApiToken()
            }
        ).then((group_info)=>{
            showDialog({
                title: 'Submit Notebook as Job',
                body: new JobInfoInput(group_info),
                buttons: [Dialog.cancelButton(), Dialog.okButton({label: 'Submit'})]
            }).then((result) => {
                console.log(result);
                if (result.button.label === "Cancel")
                    return;
                //if (result.value.jobName.length === 0)
                //    console.log('empty job name');
                if (result.button.accept)
                    this.submitNotebook(result.value, group_info.name);
            });
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
    
    submitNotebook = (value: any, group: string): void => {
        requestAPI<any>('submit-job', 'POST', 
            {
                'api_token': this.getApiToken(),
                'name': value.jobName,
                'instance_type': value.instanceType,
                'image': value.image,
                'path': this.getNodebookPath(),
                'group_name': group
            }
        ).then((result)=>{
            console.log(result);
            let jobMsg;
            if (result.status === 'success') {
                jobMsg = `${value.jobName} has been submitted! You can ` + 
                    `<a href="/console/g/${group}/job/${result.job_id}" target="_blank"><u>view your job details here.</u></a>`;
            }
            else {/* handling error conditions */}

            showDialog({
                title: result.status === 'success' ? 'Success' : 'Failed',
                body: new SubmitJobResult(jobMsg),
                buttons: [Dialog.okButton()]
            }).then((result) => {});
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

export class ApiTokenInput extends ReactWidget {

    constructor(apiToken: string) {
        super();
        this.value = apiToken;
    }

    render() {
        return (
        <div>
            <label>Please fill in your API token before you submit your notebook as a job.</label>
            <br />
            <StringInputComponent value={this.value}
                handleChange={(event) => {
                    this.value = event.target.value;
                }}
            />
        </div>
        );
    }

    private value: string;

    getValue(): string {
        return this.value;
    }

}

export class JobInfoInput extends Widget {
    constructor(group_info:any) {
        super();
        // TODO use group_info to build JobSubmit UI
        console.log('here is group info:');
        console.log(group_info);

        requestAPI<any>('get-env', 'POST', {}).then((env_info)=>{
            console.log(env_info);
        /*
        this.groupResourceLabel = document.createElement('label');
        this.groupResourceLabel.innerHTML = 'Group Resources';
        this.groupResourceLabel.style.marginTop = "20px";

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
        this.itLabel = document.createElement('label');
        this.itLabel.innerHTML = '* Instance Type';
        this.itLabel.style.marginTop = "20px";
        
        this.itSelector = document.createElement('select');
        let opt;
        for (let i = 0; i < group_info.instanceTypes.length; i++) {
            opt = document.createElement('option');
            opt.setAttribute('value', group_info.instanceTypes[i].name);
            opt.innerHTML = `${group_info.instanceTypes[i].displayName||group_info.instanceTypes[i].name} 
                (CPU: ${group_info.instanceTypes[i].spec['limits.cpu']} / 
                Memory: ${group_info.instanceTypes[i].spec['limits.memory']} / 
                GPU: ${group_info.instanceTypes[i].spec['limits.nvidia.com/gpu']})`;
            this.itSelector.appendChild(opt);

            if (env_info.instanceType === group_info.instanceTypes[i].name) this.itSelector.selectedIndex = i;
        }

        this.imageLabel = document.createElement('label');
        this.imageLabel.innerHTML = '* Image';
        this.imageLabel.style.marginTop = "20px";
        
        this.imageSelector = document.createElement('select');
        for (let i = 0; i < group_info.images.length; i++) {
            opt = document.createElement('option');
            opt.setAttribute('value', group_info.images[i].name);
            opt.innerHTML = `${group_info.images[i].displayName||group_info.images[i].name} 
                (${group_info.images[i].spec['type'] === 'both' ? 'Universal' : group_info.images[i].spec['type'].toUpperCase()})`;
            this.imageSelector.appendChild(opt);

            if (env_info.image === group_info.images[i].name) this.imageSelector.selectedIndex = i;
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

        //this.npLink = document.createElement('link');
        //this.npLink.innerHTML = '?';
        //this.npLink.href = 'https://docs.primehub.io/';
        
        this.npTextArea = document.createElement('textarea');
        this.npTextArea.placeholder = 'alpha = 0.1; ratio = 0.1';
        
        //this.node.appendChild(this.groupResourceLabel);
        //this.node.appendChild(this.groupResourceTable);
        this.node.appendChild(this.itLabel);
        this.node.appendChild(this.itSelector);
        this.node.appendChild(this.imageLabel);
        this.node.appendChild(this.imageSelector);
        this.node.appendChild(this.nameLabel);
        this.node.appendChild(this.nameInput);
        this.node.appendChild(this.npLabel);
        //this.node.appendChild(this.npLink);
        this.node.appendChild(this.npTextArea);
        });
    }

    getValue(): any {
        const values: { [key: string]: string; } = {};
        values["instanceType"] = this.itSelector.value.toString();
        values["image"] = this.imageSelector.value.toString();
        values["jobName"] = this.nameInput.value.trim();
        values["notebookParameters"] = this.npTextArea.value.toString();

        return values;
    }
    
    //protected groupResourceLabel: HTMLLabelElement;
    //protected groupResourceTable: HTMLTableElement;
    protected itLabel: HTMLLabelElement;
    protected itSelector: HTMLSelectElement;
    protected imageLabel: HTMLLabelElement;
    protected imageSelector: HTMLSelectElement;
    protected nameLabel: HTMLLabelElement;
    protected nameInput: HTMLInputElement;
    protected npLabel: HTMLLabelElement;
    //protected npLink: HTMLLinkElement;
    protected npTextArea: HTMLTextAreaElement;
}

export class SubmitJobResult extends Widget {
    constructor(jobMsg: string) {
        super();
        this.infoLabel = document.createElement('label');
        this.infoLabel.innerHTML = jobMsg;
        this.node.appendChild(this.infoLabel);
    }
    protected infoLabel: HTMLLabelElement;
}
