import { Component } from '@angular/core';
import { YatraService } from '../service/yatra.service';

@Component({
  selector: 'app-yatra-gpt',
  templateUrl: './yatra-gpt.component.html',
  styleUrls: ['./yatra-gpt.component.css'],
})
export class YatraGptComponent {
  userMessage: string = '';
  messages: { user: string; ai: string }[] = [];
  editingIndex: number | null = null;
  private typingInterval: any;
  isTyping: boolean = false;
  showWarningMessage: boolean = false;

  showModal: boolean = false;
  recording: boolean = false;
  timer: number = 0;
  interval: any;
  private mediaStream: MediaStream | null = null;

  constructor(private yatraService: YatraService) {}

  modelDescriptions: { [key: string]: string } = {
    'Yatra Core':
      'Le modèle essentiel, conçu pour des tâches de base avec un dataset limité.',
    'Yatra Boost':
      'Modèle avec un dataset plus robuste (non disponible actuellement).',
    'Yatra Polyglot':
      "Modèle capable de reconnaître jusqu'à 20 langues (non disponible actuellement).",
    'Yatra Turbo':
      'Modèle très rapide avec des données complètes (non disponible actuellement).',
  };

  updateModelDescription(event: Event) {
    const selectElement = event.target as HTMLSelectElement;
    const selectedModel = selectElement.value;
    console.log(`Modèle sélectionné: ${selectedModel}`);
  }

  sendMessage() {
    if (!this.userMessage.trim()) return;

    this.messages.push({ user: this.userMessage, ai: '' });
    this.isTyping = true;

    // Appel du service pour envoyer la requête au backend
    this.yatraService.processMessage(this.userMessage).subscribe({
      next: (response) => {
        const entities = response.entities;
        const path = response.path;
        const totalDuration = response.total_duration;

        // Liste des phrases possibles pour une compréhension réussie
        const successPhrases = [
          `Super, j'ai trouvé un itinéraire pour toi : ${path.join(
            ' -> '
          )}. Ça prendra environ ${totalDuration} minutes.`,
          `Voilà ce que j'ai trouvé comme itinéraire : ${path.join(
            ' -> '
          )}. Tu seras à destination en environ ${totalDuration} minutes.`,
          `Je t'ai déniché un trajet : ${path.join(
            ' -> '
          )}. Compte environ ${totalDuration} minutes pour le parcours.`,
          `Check ça ! Voici un trajet : ${path.join(
            ' -> '
          )}. Il te faudra environ ${totalDuration} minutes.`,
          `C'est tout bon, voici le chemin : ${path.join(
            ' -> '
          )}. Cela prendra environ ${totalDuration} minutes.`,
          `Voici ce que j'ai trouvé pour toi : ${path.join(
            ' -> '
          )}. Prépare-toi à environ ${totalDuration} minutes de trajet.`,
          `Tu peux suivre ce parcours : ${path.join(
            ' -> '
          )}. La durée totale sera d'environ ${totalDuration} minutes.`,
          `J'ai trouvé un itinéraire : ${path.join(
            ' -> '
          )}. Attends-toi à environ ${totalDuration} minutes pour le trajet.`,
          `Voici l'itinéraire que j'ai trouvé : ${path.join(
            ' -> '
          )}. Le trajet devrait durer environ ${totalDuration} minutes.`,
          `J'ai une suggestion pour toi : ${path.join(
            ' -> '
          )}. Cela prendra environ ${totalDuration} minutes.`,
        ];

        // Liste des phrases possibles pour les incompréhensions
        const errorPhrases = [
          "Je n'ai pas tout compris, pourrais-tu reformuler ta demande ?",
          "Désolé, je n'arrive pas à saisir ce que tu veux dire. Peux-tu expliquer autrement ?",
          'Hmm, il semble y avoir un malentendu. Pourrais-tu préciser ?',
          "Oups, je n'ai pas bien saisi. Peux-tu reformuler ta phrase ?",
          'Je crois que je ne comprends pas tout. Pourrais-tu clarifier ?',
          'Désolé, je ne suis pas sûr de ce que tu demandes. Peux-tu être plus précis ?',
          "Je n'ai pas bien saisi. Peux-tu reformuler ta question, s'il te plaît ?",
          'Je suis un peu perdu. Pourrais-tu être plus clair ?',
          'Je ne suis pas sûr de comprendre. Est-ce que tu peux expliquer différemment ?',
          "Désolé, je n'ai pas compris. Tu pourrais reformuler ta demande ?",
        ];

        // Si un chemin est trouvé, choisir une phrase parmi les phrases de succès
        let aiResponse = '';
        if (path && path.length > 0) {
          const randomPhrase =
            successPhrases[Math.floor(Math.random() * successPhrases.length)];
          aiResponse += `\n${randomPhrase}`;
        } else {
          // Sinon, choisir une phrase parmi les phrases d'erreur
          const randomErrorPhrase =
            errorPhrases[Math.floor(Math.random() * errorPhrases.length)];
          aiResponse = randomErrorPhrase;
        }

        // Ajout de la durée de trajet si le chemin existe, sans répéter
        if (totalDuration !== null && path && path.length > 0) {
          // La durée est déjà incluse dans la phrase choisie dans successPhrases, donc pas besoin de l'ajouter à nouveau
        } else {
          aiResponse += `\nHmm, je n'ai pas pu estimer la durée pour le moment.`;
        }

        // Ajout de la réponse au tableau de messages
        this.simulateTyping(aiResponse, this.messages.length - 1);
      },
      error: (err) => {
        console.error('Erreur de traitement:', err);
        this.isTyping = false;
        this.messages[this.messages.length - 1].ai =
          'Désolé, quelque chose ne va pas. Laisse-moi essayer à nouveau.';
      },
    });
  }

  editMessage(index: number) {
    this.userMessage = this.messages[index].user;
    this.editingIndex = index;
  }

  private simulateTyping(response: string, messageIndex: number) {
    let index = 0;
    this.typingInterval = setInterval(() => {
      if (index < response.length) {
        this.messages[messageIndex].ai += response.charAt(index);
        index++;
      } else {
        clearInterval(this.typingInterval);
        this.isTyping = false;
      }
    }, 50);
  }

  stopTyping() {
    clearInterval(this.typingInterval);
    this.isTyping = false;
  }

  displayWarningMessage() {
    this.showWarningMessage = true;
    setTimeout(() => {
      const warningMessageElement = document.querySelector('.warning-message');
      if (warningMessageElement) {
        warningMessageElement.classList.add('fade-out');
        setTimeout(() => {
          this.showWarningMessage = false;
          warningMessageElement.classList.remove('fade-out');
        }, 500);
      }
    }, 2000);
  }

  setFeatureMessage(feature: string) {
    this.userMessage = feature;
  }

  openMicrophoneModal() {
    this.showModal = true;
    this.startRecording();
  }

  closeMicrophoneModal() {
    this.stopRecording();
    this.showModal = false;
  }

  startRecording() {
    this.timer = 0;
    this.recording = true;
    this.interval = setInterval(() => {
      this.timer += 1;
    }, 1000);

    navigator.mediaDevices
      .getUserMedia({ audio: true })
      .then((stream) => {
        this.mediaStream = stream;
        console.log('Microphone is on', stream);
      })
      .catch((err) => {
        console.error('Error accessing the microphone', err);
        this.stopRecording();
      });
  }

  stopRecording() {
    this.recording = false;
    clearInterval(this.interval);
    if (this.mediaStream) {
      const tracks = this.mediaStream.getTracks();
      tracks.forEach((track) => track.stop());
      this.mediaStream = null;
    }
    this.showModal = false;
  }
}
