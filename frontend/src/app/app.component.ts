import { Component } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrl: './app.component.css',
})
export class AppComponent {
  title = 'yatra-gpt';

  constructor(private router: Router) {}

  ngOnInit(): void {}

  goToHome() {
    this.router.navigate(['']);
  }

  startChat() {
    this.router.navigate(['yatra-gpt']);
  }

  goToModelsAbout() {
    this.router.navigate(['models-about']);
  }
}
