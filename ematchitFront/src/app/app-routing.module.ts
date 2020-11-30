import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { HomeComponent } from './home/home.component';
import { NotfoundComponent } from './notfound/notfound.component';
import { LoginComponent } from './login/login.component';
import { AuthGuard } from './auth.guard';


const routes: Routes = [
  {path : 'home', component : HomeComponent},
  {path : '', redirectTo:'/home', pathMatch:'full'}, 
  {path : 'login', component : LoginComponent},
  {path: 'parser', loadChildren: () => import('./parser/parser.module').then(m => m.ParserModule),
  canActivate: [AuthGuard] },
  {path: '**', component : NotfoundComponent }
];


@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})

export class AppRoutingModule { }
export const RoutingComponents = [HomeComponent, LoginComponent, NotfoundComponent]
