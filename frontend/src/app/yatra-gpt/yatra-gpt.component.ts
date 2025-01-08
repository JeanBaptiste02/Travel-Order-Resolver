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
    if (this.userMessage.trim()) {
      // Ajouter le message de l'utilisateur dans les messages
      const userMessageIndex = this.messages.length;
      this.messages.push({
        user: this.userMessage,
        ai: 'Traitement en cours...',
      });

      console.log("Message de l'utilisateur:", this.userMessage); // Log du message initial

      // Appeler l'endpoint `detect_language`
      this.yatraService.detectLanguage(this.userMessage).subscribe(
        (languageResponse) => {
          const detectedLanguage = languageResponse.language;

          // Mettre à jour la réponse AI avec la langue détectée
          this.messages[userMessageIndex].ai =
            `Langue détectée : ${detectedLanguage}\n` + this.userMessage;

          // Vérifier si la langue est bien le français
          if (detectedLanguage !== 'French') {
            this.messages[
              userMessageIndex
            ].ai += `\nLa langue détectée n'est pas le français. Arrêt.\n`;
            return;
          }

          console.log(
            'Message après détection de la langue:',
            this.userMessage
          ); // Toujours le même message

          // Passer directement à la détection des entités
          this.yatraService.predictEntities(this.userMessage).subscribe(
            (entitiesResponse) => {
              const entities = entitiesResponse.entities || [];
              this.messages[
                userMessageIndex
              ].ai += `Entités détectées : ${entities.join(', ')}\n`;

              // Si 2 entités sont détectées, trouver le trajet
              if (entities.length >= 2) {
                const depart = entities[0];
                const arrivee = entities[1];

                // Trouver le chemin entre les deux entités
                this.yatraService.findPath(depart, arrivee).subscribe(
                  (pathResponse) => {
                    if (pathResponse.path && pathResponse.path.length > 0) {
                      this.messages[
                        userMessageIndex
                      ].ai += `Trajet trouvé : ${pathResponse.path.join(
                        ' -> '
                      )}\n`;
                      this.messages[
                        userMessageIndex
                      ].ai += `Durée totale : ${pathResponse.total_duration} minutes\n`;
                    } else {
                      this.messages[
                        userMessageIndex
                      ].ai += `Aucun trajet trouvé entre ${depart} et ${arrivee}.\n`;
                    }
                  },
                  (error) => {
                    console.error(
                      'Erreur lors de la recherche de chemin :',
                      error
                    );
                    this.messages[
                      userMessageIndex
                    ].ai += `Erreur lors de la recherche de chemin.\n`;
                  }
                );
              } else {
                this.messages[
                  userMessageIndex
                ].ai += `Pas assez d'entités détectées pour trouver un trajet.\n`;
              }
            },
            (error) => {
              console.error('Erreur lors de la détection des entités :', error);
              this.messages[
                userMessageIndex
              ].ai += `Erreur lors de la détection des entités.\n`;
            }
          );
        },
        (error) => {
          console.error('Erreur lors de la détection de la langue :', error);
          this.messages[
            userMessageIndex
          ].ai += `Erreur lors de la détection de la langue.\n`;
        }
      );

      // Réinitialiser l'input après tout le traitement (après les appels API)
      this.displayWarningMessage(); // Afficher l'avertissement
      this.userMessage = ''; // Réinitialiser l'input après tout le processus
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
