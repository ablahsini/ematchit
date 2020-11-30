import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

import { ParserComponent } from './parser.component';

const routes: Routes = [{ path: '', component: ParserComponent }];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class ParserRoutingModule { }
