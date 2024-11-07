import { Component } from '@angular/core';

@Component({
  selector: 'app-models',
  templateUrl: './models.component.html',
  styleUrl: './models.component.css',
})
export class ModelsComponent {
  models = [
    {
      name: 'Yatra Core',
      description:
        'Le modèle essentiel, conçu pour des tâches de base avec un dataset limité.',
      comingSoon: false,
    },
    {
      name: 'Yatra Boost',
      description:
        'Modèle avec un dataset plus robuste (non disponible actuellement).',
      comingSoon: true,
    },
    {
      name: 'Yatra Polyglot',
      description:
        "Modèle capable de reconnaître jusqu'à 20 langues (non disponible actuellement).",
      comingSoon: true,
    },
    {
      name: 'Yatra Turbo',
      description:
        'Modèle très rapide avec des données complètes (non disponible actuellement).',
      comingSoon: true,
    },
  ];
}
