import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { HomePageComponent } from './home-page/home-page.component';
import { YatraGptComponent } from './yatra-gpt/yatra-gpt.component';
import { ModelsComponent } from './models/models.component';

const routes: Routes = [
  { path: '', component: HomePageComponent },
  { path: 'yatra-gpt', component: YatraGptComponent },
  { path: 'models-about', component: ModelsComponent },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule],
})
export class AppRoutingModule {}
