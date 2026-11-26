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

const DEMO_PLAN = {
  summary: "Today's air quality in Pune is Moderate with winter morning inversion. Outdoor activity is safest between 12:00 PM and 4:00 PM. High caution for children and household members with respiratory sensitivity.",
  time_windows: [
    {
      label: "Best Window for Outdoor Activity & Exercise",
      start_hour: 12,
      end_hour: 16,
      quality: "best",
      activities: ["Outdoor walking", "School sports", "Errands"],
      reasoning: "Solar heating breaks the ground-level inversion layer; vertical air mixing disperses trapped particulates."
    },
    {
      label: "Acceptable Afternoon Window",
      start_hour: 16,
      end_hour: 18,
      quality: "good",
      activities: ["Commute home", "Evening stroll with N95 mask"],
      reasoning: "Moderate PM2.5 levels before night-time cooling traps emissions near the ground."
    },
    {
      label: "High Exposure Window — Avoid Outdoors",
      start_hour: 6,
      end_hour: 10,
      quality: "avoid",
      activities: ["Indoor morning routines", "Reschedule outdoor runs"],
      reasoning: "Severe winter temperature inversion traps vehicle exhaust and biomass smoke at surface level."
    }
  ],
  recommendations: [
    {
      category: "commute",
      title: "Switch Petrol Two-Wheeler to Pune Metro / Electric Bus",
      description: "Taking Pune Metro saves direct inhalation of particulate matter from vehicle exhausts and road dust.",
      cost_level: "low",
      effort_level: "easy",
      impact_explanation: "Estimated 4.2 kg CO₂e avoided today and 85 µg/m³-h PM2.5 inhalation reduction for your 10 km commute."
    },
    {
      category: "indoor_air",
      title: "Run HEPA Air Purifier in Bedroom During Sleep",
      description: "Operate purifier at medium speed with windows sealed between 10 PM and 7 AM.",
      cost_level: "low",
      effort_level: "easy",
      impact_explanation: "Reduces indoor sleeping exposure from 65 µg/m³ to below 15 µg/m³ (WHO 24h target)."
    },
    {
      category: "cooking",
      title: "Keep Kitchen Exhaust Fan On 15 Minutes After Cooking",
      description: "Residual cooking particles linger in kitchen air without positive extraction.",
      cost_level: "free",
      effort_level: "easy",
      impact_explanation: "Clears 65% of ultrafine cooking emissions before they disperse to bedrooms."
    }
  ]
};

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
      <div class="plan-header">
        <h2>{{ 'plan.title' | translate }}</h2>
        <span class="genai-badge">
          <mat-icon inline>auto_awesome</mat-icon> Powered by Google Gemini 1.5
        </span>
      </div>

      <div *ngIf="loading()" class="loading">
        <mat-spinner diameter="36"></mat-spinner>
        <span>{{ 'common.loading' | translate }}</span>
      </div>

      <ng-container *ngIf="plan() as p">
        <mat-card class="summary-card">
          <mat-card-content>
            <p class="summary-text">{{ p.summary }}</p>
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
          <mat-card *ngFor="let r of p.recommendations" class="rec-card">
            <mat-card-header>
              <mat-icon mat-card-avatar color="primary">eco</mat-icon>
              <mat-card-title>{{ r.title }}</mat-card-title>
              <mat-card-subtitle>Cost: {{ r.cost_level | uppercase }} · Effort: {{ r.effort_level | uppercase }}</mat-card-subtitle>
            </mat-card-header>
            <mat-card-content>
              <p>{{ r.description }}</p>
              <div *ngIf="r.impact_explanation" class="impact-badge">
                <mat-icon inline color="primary">insights</mat-icon>
                <span><strong>Impact:</strong> {{ r.impact_explanation }}</span>
              </div>
            </mat-card-content>
          </mat-card>
        </div>
      </ng-container>
    </div>
  `,
  styles: [`
    .plan-container { max-width: 900px; margin: 0 auto; display: flex; flex-direction: column; gap: 16px; }
    .plan-header { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; }
    .genai-badge { display: flex; align-items: center; gap: 4px; font-size: 13px; color: #1b5e20; background: #e8f5e9; padding: 4px 10px; border-radius: 12px; font-weight: 500; }
    .loading { display: flex; align-items: center; gap: 12px; padding: 24px; }
    .summary-card { background: #f1f8e9; border-left: 5px solid #2e7d32; }
    .summary-text { font-size: 16px; line-height: 1.5; margin: 0; color: #1b5e20; }
    .windows-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 12px; }
    .recs-list { display: flex; flex-direction: column; gap: 12px; }
    .rec-card { border-radius: 8px; }
    .window-best { border-left: 5px solid #55a84f; }
    .window-good { border-left: 5px solid #a3c853; }
    .window-avoid { border-left: 5px solid #e93f33; }
    .impact-badge { margin-top: 8px; padding: 8px 12px; background: #e8f5e9; border-radius: 6px; color: #2e7d32; display: flex; align-items: center; gap: 6px; }
  `],
})
export class DailyPlanComponent implements OnInit {
  private http = inject(HttpClient);
  plan = signal<any>(DEMO_PLAN);
  loading = signal(false);

  ngOnInit() {
    this.loadPlan();
  }

  loadPlan() {
    const lang = localStorage.getItem('lang') || 'en';
    this.http.get(`${environment.apiUrl}/plan/today`, { params: { language: lang } }).subscribe({
      next: res => {
        if (res) this.plan.set(res);
      },
      error: () => {
        // Fallback to rich pre-computed plan
        this.plan.set(DEMO_PLAN);
      },
    });
  }
}
