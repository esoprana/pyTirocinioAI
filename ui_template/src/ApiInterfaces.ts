export interface IMessage {
    id: string;
    text: string;
    timestamp: string;
    bot: boolean;
}

export interface IResponse extends IMessage {
    response: string;
}

export interface IUser {
    id: string;
    username: string;
}

interface IContextMessage {
    text: string;
}

interface IBotMessage extends IContextMessage {
    cls: 'BotMessage';
    fromRule: string;
}

interface IUserMessage extends IContextMessage {
    cls: 'UserMessage';

    photo: object;
    intent: object;
    googleTopic: any[];
    sentiment: object;
}

interface IParams {
    ofTopic: string;
    values: object;
    startTime: string;
    priority: number;
}

export interface IContext {
    params: IParams[];
    timestamp: string;
    ofUser: string;
    message: IUserMessage | IBotMessage;
}

interface IAction {
    text: string[];
    operations: object[];
    isQuestion: boolean;
    immediatlyNext: boolean;
}


export interface IRule {
    condition: object;
    score: number;
    action: IAction;
}

export interface ITopic {
    name: string;
    rules: string[];
}
