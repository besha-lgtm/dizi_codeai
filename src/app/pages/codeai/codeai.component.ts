import { Component } from '@angular/core';

interface ChatMessage {
  sender: 'ai' | 'user';
  text?: string;
  options?: string[];
}

@Component({
  selector: 'app-codeai',
  standalone: false,
  templateUrl: './codeai.component.html',
  styleUrl: './codeai.component.css'
})
export class CodeaiComponent {
  isChatOpen = false;

  isTyping = false;

  userInput = '';

  currentStep = 0;

  messages: ChatMessage[] = [];


  /* AUDIT DATA */

  gitUrl = '';

  auditType = '';

  model = '';


  /* OPEN CHAT */

  toggleChat() {

    this.isChatOpen = !this.isChatOpen;

    if (this.isChatOpen && this.messages.length === 0) {

      this.startConversation();

    }

  }


  /* START CONVERSATION */

  startConversation() {

    this.addAiMessage(
      "Hi! 👋 I'm Code AI Auditor. I'll help you analyze your repository step by step."
    );

    setTimeout(() => {

      this.addAiMessage(
        "First, please provide your Git repository URL."
      );

    }, 700);

  }


  /* SEND MESSAGE */

  sendMessage() {

    const value = this.userInput.trim();

    if (!value || this.isTyping) {
      return;
    }


    /* ADD USER MESSAGE */

    this.messages.push({
      sender: 'user',
      text: value
    });


    this.userInput = '';


    /* PROCESS RESPONSE */

    this.processUserResponse(value);

  }


  /* PROCESS USER RESPONSE */

  processUserResponse(value: string) {

    this.isTyping = true;


    setTimeout(() => {

      this.isTyping = false;


      switch (this.currentStep) {


        /* STEP 0 - GIT URL */

        case 0:

          this.gitUrl = value;

          this.currentStep = 1;

          this.addAiMessage(
            "Perfect! I've received your repository URL."
          );

          setTimeout(() => {

            this.addAiMessage(
              "What would you like me to audit?",
              [
                'Security',
                'Performance',
                'Best Practices',
                'Everything'
              ]
            );

          }, 600);

          break;


        /* STEP 1 - AUDIT TYPE */

        case 1:

          this.auditType = value;

          this.currentStep = 2;

          this.addAiMessage(
            `Great. I'll focus on ${value.toLowerCase()} analysis.`
          );

          setTimeout(() => {

            this.addAiMessage(
              "Which AI model would you like to use?",
              [
                'Gemini',
                'Claude'
              ]
            );

          }, 600);

          break;


        /* STEP 2 - MODEL */

        case 2:

          this.model = value;

          this.currentStep = 3;

          this.addAiMessage(
            `${value} selected.`
          );

          setTimeout(() => {

            this.addAiMessage(
              "I have everything I need. Shall I start the code audit?",
              [
                'Yes, start audit',
                'No, cancel'
              ]
            );

          }, 600);

          break;


        /* STEP 3 - CONFIRMATION */

        case 3:

          if (
            value.toLowerCase().includes('yes') ||
            value.toLowerCase().includes('start')
          ) {

            this.startAudit();

          } else {

            this.addAiMessage(
              "No problem. The audit has been cancelled. You can start again whenever you're ready."
            );

          }

          break;

      }

    }, 800);

  }


  /* OPTION BUTTON */

  selectOption(option: string) {

    this.messages.push({
      sender: 'user',
      text: option
    });

    this.processUserResponse(option);

  }


  /* AI MESSAGE */

  addAiMessage(
    text: string,
    options?: string[]
  ) {

    this.messages.push({
      sender: 'ai',
      text,
      options
    });

  }


  /* START AUDIT */

  startAudit() {

    this.isTyping = true;


    setTimeout(() => {

      this.isTyping = false;

      this.addAiMessage(
        "🔍 Starting repository analysis..."
      );


      setTimeout(() => {

        this.addAiMessage(
          `Repository: ${this.gitUrl}`
        );

      }, 800);


      setTimeout(() => {

        this.addAiMessage(
          `Audit type: ${this.auditType}`
        );

      }, 1400);


      setTimeout(() => {

        this.addAiMessage(
          `AI model: ${this.model}`
        );

      }, 2000);


      setTimeout(() => {

        this.addAiMessage(
          "⏳ Repository analysis is in progress. I'll report the findings here once the analysis is complete."
        );

      }, 2800);

    }, 800);

  }

}

