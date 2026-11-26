// Dashboard component — AQI overview, quick action cards, today's summary
import { Component, OnInit, inject, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatDividerModule } from '@angular/material/divider';
import { TranslateModule } from '@ngx-translate/core';
import { AqiService, AQIData } from '../../core/services/aqi.service';
import { ProfileService } from '../../core/services/profile.service';

@Component({
  selector: 'ca-dashboard',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    CommonModule, RouterLink,
    MatCardModule, MatButtonModule, MatIconModule,
    MatProgressBarModule, MatDividerModule,
    TranslateModule,
  ],
  template: `
    <div class="dashboard-grid">
      <!-- AQI Hero Card -->
      <mat-card class="aqi-hero" *ngIf="aqi$ | async as aqi">
        <mat-card-header>
          <mat-card-title>{{ 'dashboard.airQuality' | translate }}</mat-card-title>
          <mat-card-subtitle>{{ aqi.observed_at | date:'short' }}</mat-card-subtitle>
        </mat-card-header>
        <mat-card-content>
          <div class="aqi-display"
               [style.color]="getColor(aqi.aqi)"
               role="img"
               [attr.aria-label]="'AQI is ' + aqi.aqi">
            <span class="aqi-number">{{ aqi.aqi ?? '—' }}</span>
            <span class="aqi-label">{{ aqi.aqi_category }}</span>
          </div>
          <div class="pollutant-grid">
            <div class="pollutant" *ngFor="let p of pollutants(aqi)">
              <span class="p-label">{{ p.label }}</span>
              <span class="p-value">{{ p.value | number:'1.0-1' }}</span>
              <span class="p-unit">{{ p.unit }}</span>
            </div>
          </div>
          <div class="inversion-warning" *ngIf="aqi.temperature_inversion" role="alert">
            <mat-icon color="warn">warning</mat-icon>
            {{ 'dashboard.inversionWarning' | translate }}
          </div>
        </mat-card-content>
        <mat-card-actions>
          <a mat-raised-button color="primary" routerLink="/plan">
            <mat-icon>event_available</mat-icon>
            {{ 'dashboard.viewPlan' | translate }}
          </a>
          <a mat-stroked-button routerLink="/chat">
            <mat-icon>chat</mat-icon>
            {{ 'dashboard.askAssistant' | translate }}
          </a>
        </mat-card-actions>
      </mat-card>

      <!-- Quick Actions -->
      <div class="quick-actions">
        <mat-card class="action-card" routerLink="/plan" role="button" tabindex="0">
          <mat-card-content>
            <mat-icon class="action-icon" color="primary">schedule</mat-icon>
            <p>{{ 'dashboard.bestTime' | translate }}</p>
          </mat-card-content>
        </mat-card>
        <mat-card class="action-card" routerLink="/chat" role="button" tabindex="0">
          <mat-card-content>
            <mat-icon class="action-icon" style="color:#55a84f">psychology</mat-icon>
            <p>{{ 'dashboard.askAI' | translate }}</p>
          </mat-card-content>
        </mat-card>
        <mat-card class="action-card" routerLink="/community" role="button" tabindex="0">
          <mat-card-content>
            <mat-icon class="action-icon" color="accent">group</mat-icon>
            <p>{{ 'dashboard.community' | translate }}</p>
          </mat-card-content>
        </mat-card>
      </div>

      <!-- Indoor tips (static fast-load) -->
      <mat-card class="indoor-tips">
        <mat-card-header>
          <mat-icon mat-card-avatar>home</mat-icon>
          <mat-card-title>{{ 'dashboard.indoorTips' | translate }}</mat-card-title>
        </mat-card-header>
        <mat-card-content>
          <ul class="tips-list">
            <li *ngFor="let tip of indoorTips">{{ tip | translate }}</li>
          </ul>
        </mat-card-content>
      </mat-card>
    </div>
  `,
  styles: [`
    .dashboard-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      grid-template-rows: auto auto;
      gap: 16px;
    }
    .aqi-hero { grid-column: 1 / -1; }
    .aqi-display { display: flex; align-items: baseline; gap: 12px; margin: 16px 0; }
    .aqi-number { font-size: 72px; font-weight: 900; line-height: 1; }
    .aqi-label { font-size: 24px; font-weight: 500; }
    .pollutant-grid { display: flex; gap: 24px; flex-wrap: wrap; margin-top: 8px; }
    .pollutant { display: flex; flex-direction: column; align-items: center; }
    .p-label { font-size: 11px; color: #666; text-transform: uppercase; }
    .p-value { font-size: 20px; font-weight: 700; }
    .p-unit { font-size: 11px; color: #666; }
    .inversion-warning {
      display: flex; align-items: center; gap: 8px;
      background: #fff3e0; padding: 8px 12px; border-radius: 4px;
      margin-top: 12px; color: #e65100;
    }
    .quick-actions { grid-column: 1 / -1; display: flex; gap: 12px; }
    .action-card {
      flex: 1; cursor: pointer; text-align: center;
      transition: box-shadow 0.2s;
    }
    .action-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,.2); }
    .action-icon { font-size: 36px; height: 36px; width: 36px; }
    .tips-list { margin: 0; padding-left: 20px; }
    .tips-list li { margin-bottom: 8px; }
    @media (max-width: 600px) {
      .dashboard-grid { grid-template-columns: 1fr; }
      .aqi-number { font-size: 48px; }
      .quick-actions { flex-direction: column; }
    }
  `]
})
export class DashboardComponent implements OnInit {
  private aqiSvc = inject(AqiService);
  private profileSvc = inject(ProfileService);
  readonly aqi$ = this.aqiSvc.aqi$;

  readonly indoorTips = [
    'tips.closeWindowsMorning',
    'tips.useKitchenExhaust',
    'tips.avoidIncenseSmoke',
    'tips.plantsModerateBenefit',
  ];

  ngOnInit() {
    const p = this.profileSvc.current;
    this.aqiSvc.fetchAQI(p?.latitude ?? 18.52, p?.longitude ?? 73.85).subscribe();
  }

  getColor(aqi: number | null): string { return AqiService.aqiColor(aqi); }

  pollutants(aqi: AQIData) {
    return [
      { label: 'PM2.5', value: aqi.pm25, unit: 'µg/m³' },
      { label: 'PM10',  value: aqi.pm10, unit: 'µg/m³' },
      { label: 'NO₂',   value: aqi.no2,  unit: 'µg/m³' },
      { label: 'Temp',  value: aqi.temperature_c, unit: '°C' },
      { label: 'RH',    value: aqi.humidity_pct,  unit: '%'  },
    ].filter(p => p.value !== null);
  }
}

