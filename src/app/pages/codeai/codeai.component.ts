import { Component, OnDestroy } from '@angular/core';
import { Subscription } from 'rxjs';
import { CodeAiService, ReviewFile } from './codeai.service';

interface ChatMessage {
  sender: 'ai' | 'user';
  text?: string;
  options?: string[];
  isReport?: boolean;
  reportData?: ReviewFile[];
  summary?: string;
  overallStatus?: 'good' | 'issues_found';
}

@Component({
  selector: 'app-codeai',
  standalone: false,
  templateUrl: './codeai.component.html',
  styleUrl: './codeai.component.css',
})
export class CodeaiComponent implements OnDestroy {

  isChatOpen = false;
  isTyping = false;
  userInput = '';
  currentStep = 0;
  messages: ChatMessage[] = [];

  /* AUDIT DATA */
  gitUrl = '';
  auditType = '';
  model = '';

  private pollSub?: Subscription;

  constructor(private codeAiService: CodeAiService) {}

  ngOnDestroy() {
    this.pollSub?.unsubscribe();
  }

  /* ─── OPEN / CLOSE CHAT ─── */

  toggleChat() {
    this.isChatOpen = !this.isChatOpen;
    if (this.isChatOpen && this.messages.length === 0) {
      this.startConversation();
    }
  }

  /* ─── STEP 0 — GREETING ─── */

  startConversation() {
    this.addAiMessage("Hi! 👋 I'm Code AI Auditor. I'll help you analyze your repository step by step.");
    setTimeout(() => {
      this.addAiMessage('First, please provide your Git repository URL.');
    }, 700);
  }

  /* ─── SEND ─── */

  sendMessage() {
    const value = this.userInput.trim();
    if (!value || this.isTyping) return;
    this.messages.push({ sender: 'user', text: value });
    this.userInput = '';
    this.processUserResponse(value);
  }

  /* ─── OPTION CLICK ─── */

  selectOption(option: string) {
    this.messages.push({ sender: 'user', text: option });
    this.processUserResponse(option);
  }

  /* ─── CONVERSATION STATE MACHINE ─── */

  processUserResponse(value: string) {
    this.isTyping = true;

    setTimeout(() => {
      this.isTyping = false;

      switch (this.currentStep) {

        // STEP 0 — collect repo URL
        case 0:
          this.gitUrl = value;
          this.currentStep = 1;
          this.addAiMessage("Perfect! I've received your repository URL.");
          setTimeout(() => {
            this.addAiMessage('What would you like me to audit?', [
              'Security',
              'Performance',
              'Best Practices',
              'Everything',
            ]);
          }, 600);
          break;

        // STEP 1 — collect audit type
        case 1:
          this.auditType = value;
          this.currentStep = 2;
          this.addAiMessage(`Great. I'll focus on **${value}** analysis.`);
          setTimeout(() => {
            this.addAiMessage('Which AI model would you like to use?', [
              'Gemini',
              'Claude',
              'Chat GPT',
            ]);
          }, 600);
          break;

        // STEP 2 — collect model
        case 2:
          this.model = value;
          this.currentStep = 3;
          this.addAiMessage(`${value} selected.`);
          setTimeout(() => {
            this.addAiMessage('I have everything I need. Shall I start the code audit?', [
              'Yes, start audit',
              'No, cancel',
            ]);
          }, 600);
          break;

        // STEP 3 — confirmation
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

  /* ─── START REAL AUDIT ─── */

  startAudit() {
    this.isTyping = true;

    this.addAiMessage('🔍 Starting repository analysis...');

    this.codeAiService.startReview(this.gitUrl, this.auditType, this.model).subscribe({
      next: (startRes) => {
        const jobId = startRes.job_id;
        this.addAiMessage('⏳ Repository cloned. Analyzing code with AI — this may take a minute...');

        // Poll every 3 s
        this.pollSub = this.codeAiService.pollUntilDone(jobId).subscribe({
          next: (job) => {
            if (job.status === 'completed' && job.result) {
              this.isTyping = false;
              this.handleReviewResult(job.result);
            } else if (job.status === 'failed') {
              this.isTyping = false;
              this.addAiMessage(`❌ Review failed: ${job.error || 'Unknown error'}`);
            }
          },
          error: (err) => {
            this.isTyping = false;
            this.addAiMessage('❌ Could not reach the backend. Make sure the Python server is running on port 8000.');
            console.error(err);
          },
        });
      },
      error: (err) => {
        this.isTyping = false;
        this.addAiMessage('❌ Could not reach the backend. Make sure the Python server is running on port 8000.');
        console.error(err);
      },
    });
  }

  /* ─── DISPLAY RESULTS ─── */

  handleReviewResult(result: any) {
    const totalIssues = (result.files || []).reduce(
      (acc: number, f: ReviewFile) => acc + (f.issues?.length || 0),
      0
    );

    if (result.overall_status === 'good') {
      this.addAiMessage(
        `✅ **Code looks great!** Reviewed **${result.files_processed}** files — no issues found.\n\n📝 ${result.summary}`
      );
      return;
    }

    // Issues found — show summary first
    this.addAiMessage(
      `⚠️ Review complete. Found **${totalIssues} issue(s)** across **${result.files_processed} file(s)**.\n\n📝 ${result.summary}`
    );

    // Then add the detailed report card
    setTimeout(() => {
      this.messages.push({
        sender: 'ai',
        isReport: true,
        overallStatus: result.overall_status,
        summary: result.summary,
        reportData: result.files,
      });
    }, 800);
  }

  /* ─── HELPERS ─── */

  addAiMessage(text: string, options?: string[]) {
    this.messages.push({ sender: 'ai', text, options });
  }

  totalIssuesFor(file: ReviewFile): number {
    return file.issues?.length || 0;
  }
}
