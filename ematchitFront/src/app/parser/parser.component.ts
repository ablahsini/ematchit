import { Component, OnInit } from '@angular/core';
import { HttpClient, HttpEventType } from '@angular/common/http';
import { Router } from '@angular/router';
import { ApiService } from '../api.service';
import { AuthService} from '../auth.service';
import { saveAs } from 'file-saver';


@Component({
  selector: 'app-parser',
  templateUrl: './parser.component.html',
  styleUrls: ['./parser.component.css']
})
export class ParserComponent implements OnInit {

formData : FormData
fileUploadProgress: string = null;
resumeName : string = 'pdf or docx ...';
loadedResume : boolean = false
edit : boolean = false;
cvOwner: String;
email: String;
phone: String;
skills: String;
education: String ;
experience: String;
loaded : number = 0
total : number = 0
misc: String;
others: String;
constructor(private apiService:ApiService, 
            private authService:AuthService,
            private router: Router) { }
 
fileProgress(fileInput: any) {
    this.formData = new FormData(); 
    const resume = <File>fileInput.target.files[0];
    this.formData.append('file', resume);
    if (this.authService.isAuthenticated()) {
      this.formData.append('username', this.authService.getUsername());
    }
    else
    {
      this.router.navigate(['/login']);
    }
    
    this.resumeName = resume.name
    this.loadedResume = true
}

onExport() {
  let cat = {"skills": this.skills,
            "education": this.education,
            "experience" : this.experience,
            "misc" : this.misc,
            "name" : this.cvOwner,
            "email" : this.email,
            "phone" : this.phone,
            "others" : this.others};
  this.apiService.ExportCategories(cat).subscribe(data => saveAs(data.body, 
                  "CV_" + this.cvOwner + ".docx"));
}

onSubmit(toto : any) {
  toto.preventDefault();
  this.fileUploadProgress = '0%';

  this.apiService.uploadResume(this.formData)
  .subscribe(
    (event)  => {
    if(event.type === HttpEventType.UploadProgress) 
    {
      this.fileUploadProgress = Math.round(event.loaded / event.total * 100) + '%';
      console.log('progress is ' + this.fileUploadProgress);
      console.log(event);
    } 
    else if(event.type === HttpEventType.Response) 
    {
      this.fileUploadProgress = '';         
      //alert('Uploaded succesfully');
      console.log(event)
      this.edit=true;
      this.skills = event.body.blocs.skills
      this.education = event.body.blocs.education
      this.experience = event.body.blocs.xp
      this.others = event.body.blocs.nocat
      this.misc = event.body.blocs.others
      this.email = event.body.blocs.email
      this.phone = event.body.blocs.phone
      console.log(this.misc)
      console.log(this.education)
    }      
  })
}

onLoadInventory(){
  if (this.authService.isAuthenticated()) {
    let username = this.authService.getUsername();
    
    this.apiService.getInventory(username).subscribe(data => console.log(data))
  }
  else
    {
      this.router.navigate(['/login']);
    }
}

  ngOnInit(): void {
  }

}
