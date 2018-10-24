export default class Api {
    private static _instance: Api|undefined = undefined;

    private url: string;

    constructor(url: string) {
        this.url = url.endsWith('/') ? url.slice(0, -1) : url;
    }

    public static init(url: string) {
        this._instance = new Api(url);
    }

    public static get Instance(): Api {
        if (this._instance === undefined) {
            throw new Error('ApiClient not initialized(use ApiClient.init(url: string))');
        }

        return this._instance
    }

    public getContext(id: string) {
        const url = `${this.url}/context/${id}`;

        return fetch(url).then( (x) => x.json() );
    }

    public getMessages(userId: string, after: string|undefined) {
        const url = `${this.url}/message/user/${userId}${after === undefined? '': ('?after=' + encodeURIComponent(after))}`;

        return fetch(url).then( (x) => x.json() ).then( (x) => x.reverse() );
    }

    public getUsers() {
        const url = `${this.url}/user/`;

        return fetch(url).then( (x) => x.json() );
    }

    public sendMessage(id: number, msg: string) {
        const url = `${this.url}/message/${id}/000000000000000000000001`

        return fetch(url, {
            method: 'PUT',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                'text': msg,
            }),
        }).then( (x) => x.json() );
    }

    public createUser(username: string) {
        const url = `${this.url}/user`;

        return fetch(url, {
            method: 'PUT',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username,
            }),
        }).then( (user) => user.json() );
    }

    public getRule(id: string) {
        const url = `${this.url}/rule/${id}`;

        return fetch(url).then( (x) => x.json() );
    }

    public getTopic(id: string) {
        const url = `${this.url}/topic/${id}`;

        return fetch(url).then( (x) => x.json() );
    }
}
