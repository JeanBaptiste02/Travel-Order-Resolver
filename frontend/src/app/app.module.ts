import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { YatraGptComponent } from './yatra-gpt/yatra-gpt.component';
import { HomePageComponent } from './home-page/home-page.component';
import { AboutPageComponent } from './about-page/about-page.component';
import { MatTooltipModule } from '@angular/material/tooltip';
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';
import { ModelsComponent } from './models/models.component';

@NgModule({
  declarations: [
    AppComponent,
    YatraGptComponent,
    HomePageComponent,
    AboutPageComponent,
    ModelsComponent,
  ],
  imports: [BrowserModule, AppRoutingModule, FormsModule, MatTooltipModule],
  providers: [provideAnimationsAsync()],
  bootstrap: [AppComponent],
})
export class AppModule {}
