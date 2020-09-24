
import React, {Component} from 'react';

export interface InputOptions {
    value: string;
    handleChange(event: React.ChangeEvent<HTMLInputElement>): void;
}

export class StringInputComponent extends Component<InputOptions> {
    constructor(options:InputOptions){
        super(options);
    }

    render() {
        return (
            <div>
                <input className='jp-mod-styled' style={{width: '100%', marginTop: '10px'}} 
                    defaultValue={this.props.value} 
                    onChange={
                        (event) => {this.handleChange(event);}
                    } />
            </div>
        )
    }

    handleChange(event: React.ChangeEvent<HTMLInputElement>) {
        this.props.handleChange(event);
    }
}