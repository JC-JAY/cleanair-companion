// Chat component — conversational AI with RAG-grounded responses
import {
  Component, OnInit, ViewChild, ElementRef, inject,
  ChangeDetectionStrategy, signal
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormControl, Validators } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatChipsModule } from '@angular/material/chips';
import { TranslateModule } from '@ngx-translate/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';

interface ChatMessage { role: 'user' | 'assistant'; content: string; }
interface ChatResponse {
  reply: string;
  citations: { title: string; url?: string; type: string }[];
  is_grounded: boolean;
  not_grounded: boolean;
  is_medical_escalation: boolean;
}

@Component({
  selector: 'ca-chat',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    CommonModule, ReactiveFormsModule,
    MatCardModule, MatInputModule, MatButtonModule,
    MatIconModule, MatProgressSpinnerModule, MatChipsModule,
    TranslateModule,
  ],
  template: `
    <div class="chat-container">
      <mat-card class="chat-card">
        <mat-card-header>
          <mat-icon mat-card-avatar color="primary">psychology</mat-icon>
          <mat-card-title>{{ 'chat.title' | translate }}</mat-card-title>
          <mat-card-subtitle>{{ 'chat.subtitle' | translate }}</mat-card-subtitle>
        </mat-card-header>

        <mat-card-content>
          <!-- Suggested prompts -->
          <div class="suggestions" *ngIf="messages().length === 0">
            <mat-chip *ngFor="let s of suggestions" (click)="sendMessage(s)" role="button">
              {{ s }}
            </mat-chip>
          </div>

          <!-- Message history -->
          <div class="messages" #messagesContainer role="log" aria-live="polite" aria-label="Chat history">
            <div *ngFor="let msg of messages()"
                 class="message"
                 [class.user-message]="msg.role === 'user'"
                 [class.assistant-message]="msg.role === 'assistant'">
              <mat-icon class="msg-icon">{{ msg.role === 'user' ? 'person' : 'eco' }}</mat-icon>
              <div class="msg-bubble">
                <p class="msg-text">{{ msg.content }}</p>
              </div>
            </div>

            <!-- Citations -->
            <div class="citations" *ngIf="lastCitations().length > 0">
              <span class="cite-label">Sources:</span>
              <a *ngFor="let c of lastCitations()"
                 [href]="c.url || '#'" target="_blank" rel="noopener noreferrer"
                 class="citation-link">{{ c.title }}</a>
            </div>

            <!-- Loading -->
            <div *ngIf="loading()" class="loading-row">
              <mat-spinner diameter="20"></mat-spinner>
              <span>{{ 'chat.thinking' | translate }}</span>
            </div>
          </div>
        </mat-card-content>

        <mat-card-actions class="input-row">
          <mat-form-field appearance="outline" class="chat-input">
            <mat-label>{{ 'chat.placeholder' | translate }}</mat-label>
            <input matInput [formControl]="inputCtrl"
                   (keydown.enter)="$event.preventDefault(); sendMessage(inputCtrl.value)"
                   [attr.aria-label]="'chat.placeholder' | translate"
                   autocomplete="off">
          </mat-form-field>
          <button mat-fab color="primary"
                  [disabled]="loading() || !inputCtrl.value?.trim()"
                  (click)="sendMessage(inputCtrl.value)"
                  [attr.aria-label]="'chat.send' | translate">
            <mat-icon>send</mat-icon>
          </button>
        </mat-card-actions>
      </mat-card>

      <!-- Disclaimer -->
      <p class="disclaimer" role="note">{{ 'common.chatDisclaimer' | translate }}</p>
    </div>
  `,
  styles: [`
    .chat-container { max-width: 760px; margin: 0 auto; }
    .chat-card { height: calc(100vh - 180px); display: flex; flex-direction: column; }
    .suggestions { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 16px; }
    .messages { flex: 1; overflow-y: auto; padding: 8px 0; display: flex; flex-direction: column; gap: 12px; }
    .message { display: flex; gap: 8px; align-items: flex-start; }
    .user-message { flex-direction: row-reverse; }
    .msg-bubble { max-width: 80%; padding: 10px 14px; border-radius: 12px; }
    .user-message .msg-bubble { background: #e3f2fd; }
    .assistant-message .msg-bubble { background: #f1f8e9; }
    .msg-text { margin: 0; white-space: pre-wrap; }
    .citations { font-size: 12px; color: #666; display: flex; flex-wrap: wrap; gap: 8px; }
    .cite-label { font-weight: 600; }
    .citation-link { color: #1565c0; text-decoration: underline; }
    .loading-row { display: flex; align-items: center; gap: 8px; color: #666; }
    .input-row { display: flex; gap: 8px; align-items: center; padding: 8px 16px; }
    .chat-input { flex: 1; }
    .disclaimer { font-size: 11px; color: #999; text-align: center; margin-top: 8px; }
  `]
})
export class ChatComponent {
  private http = inject(HttpClient);

  messages = signal<ChatMessage[]>([]);
  lastCitations = signal<any[]>([]);
  loading = signal(false);
  inputCtrl = new FormControl('', Validators.maxLength(2000));

  @ViewChild('messagesContainer') private container!: ElementRef;

  suggestions = [
    'Is it safe to exercise outdoors today?',
    'Which mask is best for PM2.5 protection?',
    'How do I improve indoor air quality cheaply?',
    'What does AQI 200 mean for my child?',
  ];

  sendMessage(text: string | null) {
    if (!text?.trim() || this.loading()) return;
    const userMsg: ChatMessage = { role: 'user', content: text.trim() };
    this.messages.update(m => [...m, userMsg]);
    this.inputCtrl.setValue('');
    this.loading.set(true);

    this.http.post<ChatResponse>(`${environment.apiUrl}/chat/`, {
      message: userMsg.content,
      history: this.messages().slice(-10),
      language: localStorage.getItem('lang') || 'en',
    }).subscribe({
      next: (res) => {
        this.messages.update(m => [...m, { role: 'assistant', content: res.reply }]);
        this.lastCitations.set(res.citations);
        this.loading.set(false);
        setTimeout(() => this.scrollBottom(), 50);
      },
      error: () => {
        this.messages.update(m => [...m, {
          role: 'assistant',
          content: 'Sorry, I could not reach the server. Please try again.'
        }]);
        this.loading.set(false);
      }
    });
  }

  private scrollBottom() {
    if (this.container) {
      this.container.nativeElement.scrollTop = this.container.nativeElement.scrollHeight;
    }
  }
}

