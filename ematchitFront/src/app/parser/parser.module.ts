import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ParserRoutingModule } from './parser-routing.module';
import { ParserComponent } from './parser.component';
import { FormsModule } from '@angular/forms';



@NgModule({
  declarations: [ParserComponent],
  imports: [
    CommonModule,
    ParserRoutingModule,
    FormsModule
  ]
})
export class ParserModule { }
