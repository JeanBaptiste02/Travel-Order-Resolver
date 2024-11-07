import { Component } from '@angular/core';

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

  // Ajoutez l'objet modelDescriptions
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

  // Méthode pour mettre à jour la description du modèle
  updateModelDescription(event: Event) {
    const selectElement = event.target as HTMLSelectElement;
    const selectedModel = selectElement.value;
    console.log(`Modèle sélectionné: ${selectedModel}`);
  }

  sendMessage() {
    if (this.userMessage.trim()) {
      if (this.editingIndex !== null) {
        this.messages[this.editingIndex].user = this.userMessage;
        this.editingIndex = null;
      } else {
        this.messages.push({ user: this.userMessage, ai: '' });
      }
      this.userMessage = '';
      this.displayWarningMessage();
      const aiResponse =
        "Je suis une réponse de l'IA ! Je suis là pour vous aider à trouver des chemins plus courts pour vos voyages !";
      this.isTyping = true;
      this.simulateTyping(aiResponse, this.messages.length - 1);
    }
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
    }, 100);
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
