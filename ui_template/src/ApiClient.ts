export default class Api {
    private static _instance: Api|undefined = undefined;

    private url: string;

    constructor(url: string) {
        this.url = url;
        if (!this.url.endsWith('/')) {
            this.url += '/';
        }
    }

    public static init(url: string) {
        this._instance = new Api(url);
    }

    public static get Instance() : Api|undefined {
        if (this._instance === undefined) {
            throw new Error('ApiClient not initialized(use ApiClient.init(url: string))');
        }

        return this._instance
    }

    public getContext(id: string) {
        return fetch(this.url + 'context/' + id).then( (x) => x.json() );
    }

    public getMessages(userId: string, after: string|undefined) {
        let url = this.url + 'message/user/' + userId;
        if (after !== undefined) {
            url += '?after=' + encodeURIComponent(after);
        }

        return fetch(url).then( (x) => x.json() ).then( (x) => x.reverse() );
    }

    public getUsers() {
        return fetch(this.url + 'user/').then( (x) => x.json() );
    }

    public sendMessage(id: number, msg: string) {
        return fetch(this.url + 'message/' + id + '/000000000000000000000001', {
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
        return fetch(this.url + 'user', {
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
        return fetch(this.url + 'rule/' + id).then( (x) => x.json() );
    }

    public getTopic(id: string) {
        return fetch(this.url + 'topic/' + id).then( (x) => x.json() );
    }
}
