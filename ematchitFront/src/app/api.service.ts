import { Injectable } from '@angular/core';
import { Resume } from './resume';
import { HttpClient, HttpHeaders, HttpResponse} from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { environment } from '../environments/environment'

@Injectable({
  providedIn: 'root'
})
export class ApiService {

  private PROCESS_API = environment.api + '/process'
  private EXPORT_API = environment.api + '/export'
  private INVENTORY_API = environment.api + '/inventory'
  
  constructor(
    private http:HttpClient
  ) { }

  uploadResume(formdata : FormData): any {
    return this.http.post(this.PROCESS_API, formdata, {
    reportProgress: true,
    observe: 'events'   
  })
}
  ExportCategories(cat : Object): any {
    console.log("calling export categories on url : ", this.EXPORT_API)
    return this.http.post(this.EXPORT_API, cat,  {observe: 'response', responseType: 'blob'})
/*     .pipe(
      map((result:HttpResponse<Blob>) => {
        console.log(result);
        return result;
      })) */
  }
  getInventory(username : string): any {
    return this.http.post(this.INVENTORY_API, {"username":username}, {
    reportProgress: true,
    observe: 'events'   
  })
}

}