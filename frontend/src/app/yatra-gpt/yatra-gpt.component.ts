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

  recognition: any; // Déclaration pour la reconnaissance vocale

  // Ajoutez la propriété recordedPhrase
  recordedPhrase: string = ''; // Nouvelle propriété pour stocker la phrase reconnue

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

    const userMessageCopy = this.userMessage;
    this.userMessage = '';

    this.yatraService.processMessage(userMessageCopy).subscribe({
      next: (response) => {
        const aiResponse = response.message;
        this.simulateTyping(aiResponse, this.messages.length - 1);
      },
      error: (err) => {
        console.error('Erreur de traitement:', err);
        this.isTyping = false;

        this.messages[this.messages.length - 1].ai =
          "Désolé, une erreur s'est produite. Veuillez réessayer.";
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

    // Initialisation de la reconnaissance vocale
    this.recognition = new (window as any).webkitSpeechRecognition();
    this.recognition.lang = 'fr-FR'; // Définir la langue (ici en français)
    this.recognition.continuous = true;
    this.recognition.interimResults = true;

    // Fonction pour mettre à jour le texte de l'utilisateur en temps réel
    this.recognition.onresult = (event: any) => {
      let transcript = '';
      for (let i = event.resultIndex; i < event.results.length; i++) {
        transcript += event.results[i][0].transcript;
      }
      this.userMessage = transcript;
    };

    this.recognition.onerror = (event: any) => {
      console.error('Erreur de reconnaissance vocale:', event.error);
      this.stopRecording();
    };

    this.recognition.start();
  }

  stopRecording() {
    this.recording = false;
    clearInterval(this.interval);
    if (this.recognition) {
      this.recognition.stop();
    }
    this.showModal = false;

    // Mise à jour de la phrase enregistrée après l'arrêt de l'enregistrement
    this.recordedPhrase = this.userMessage.trim(); // Assurez-vous de mettre à jour recordedPhrase ici

    // Une fois l'enregistrement arrêté, envoyer la phrase au backend
    if (this.recordedPhrase) {
      this.sendMessage();
    }
  }
}
