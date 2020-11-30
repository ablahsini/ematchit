export class Resume {
    id:number;
    name:string;
    file:string;

    public static fromJson(json: Object): Resume {
        var resume = new Resume()
        resume.name = json['name']
        resume.file = json['file']
        return resume;
    }
}