import { Component, OnInit, inject, ChangeDetectionStrategy, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatButtonModule } from '@angular/material/button';
import { TranslateModule } from '@ngx-translate/core';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'ca-daily-plan',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    CommonModule,
    MatCardModule,
    MatChipsModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatButtonModule,
    TranslateModule,
  ],
  template: `
    <div class="plan-container">
      <h2>{{ 'plan.title' | translate }}</h2>

      <div *ngIf="loading()" class="loading">
        <mat-spinner diameter="36"></mat-spinner>
        <span>{{ 'common.loading' | translate }}</span>
      </div>

      <div *ngIf="error()" class="error-box">
        <p>{{ error() }}</p>
        <button mat-stroked-button color="primary" (click)="loadPlan()">Retry</button>
      </div>

      <ng-container *ngIf="plan() as p">
        <mat-card class="summary-card">
          <mat-card-content>
            <p>{{ p.summary }}</p>
          </mat-card-content>
        </mat-card>

        <h3>{{ 'plan.bestWindow' | translate }}</h3>
        <div class="windows-grid">
          <mat-card *ngFor="let w of p.time_windows" [class]="'window-' + w.quality">
            <mat-card-header>
              <mat-card-title>{{ w.label }}</mat-card-title>
              <mat-card-subtitle>{{ w.start_hour }}:00 – {{ w.end_hour }}:00</mat-card-subtitle>
            </mat-card-header>
            <mat-card-content>
              <p>{{ w.reasoning }}</p>
              <mat-chip-set>
                <mat-chip *ngFor="let a of w.activities">{{ a }}</mat-chip>
              </mat-chip-set>
            </mat-card-content>
          </mat-card>
        </div>

        <h3>{{ 'plan.recommendations' | translate }}</h3>
        <div class="recs-list">
          <mat-card *ngFor="let r of p.recommendations">
            <mat-card-header>
              <mat-card-title>{{ r.title }}</mat-card-title>
              <mat-card-subtitle>Cost: {{ r.cost_level }} · Effort: {{ r.effort_level }}</mat-card-subtitle>
            </mat-card-header>
            <mat-card-content>
              <p>{{ r.description }}</p>
              <p *ngIf="r.impact_explanation" class="impact-text">{{ r.impact_explanation }}</p>
            </mat-card-content>
          </mat-card>
        </div>
      </ng-container>
    </div>
  `,
  styles: [`
    .plan-container { max-width: 900px; margin: 0 auto; display: flex; flex-direction: column; gap: 16px; }
    .loading { display: flex; align-items: center; gap: 12px; padding: 24px; }
    .windows-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 12px; }
    .recs-list { display: flex; flex-direction: column; gap: 12px; }
    .window-best { border-left: 4px solid #55a84f; }
    .window-good { border-left: 4px solid #a3c853; }
    .window-avoid { border-left: 4px solid #e93f33; }
    .impact-text { color: #2e7d32; font-weight: 500; }
  `],
})
export class DailyPlanComponent implements OnInit {
  private http = inject(HttpClient);
  plan = signal<any | null>(null);
  loading = signal(false);
  error = signal<string | null>(null);

  ngOnInit() {
    this.loadPlan();
  }

  loadPlan() {
    this.loading.set(true);
    this.error.set(null);
    const lang = localStorage.getItem('lang') || 'en';
    this.http.get(`${environment.apiUrl}/plan/today`, { params: { language: lang } }).subscribe({
      next: res => {
        this.plan.set(res);
        this.loading.set(false);
      },
      error: () => {
        this.error.set('Could not load daily plan. Ensure backend and API keys are configured.');
        this.loading.set(false);
      },
    });
  }
}

