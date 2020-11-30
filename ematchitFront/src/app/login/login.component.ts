import { Component, OnInit } from '@angular/core';
import { AuthService} from '../auth.service'
import { Router } from '@angular/router';
import { FormGroup, FormControl, Validators } from '@angular/forms';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent implements OnInit {
  message = '';
  loginForm = new FormGroup({
    username: new FormControl('', Validators.required),
    password: new FormControl('', Validators.required)
  });
  constructor(private authService:AuthService,
              private router: Router) { }

  ngOnInit(): void {
  }
  login(){
    const username = this.loginForm.get('username').value;
    const password = this.loginForm.get('password').value;
    this.authService.authenticate(username, password)
    .subscribe(
      () => {
        this.router.navigate(['/parser']);
      },
      (error) => {
        this.message = error;
      })
  }
  useDemo(){
    const username = 'demo';
    const password = 'demo';
    this.authService.authenticate(username, password)
    .subscribe(
      () => {
        this.router.navigate(['/parser']);
      },
      (error) => {
        this.message = error;
      })
  }
}
