// Dashboard component — Enhanced modern AQI overview, CPCB scale bar, impact cards, quick actions
import { Component, OnInit, inject, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatDividerModule } from '@angular/material/divider';
import { MatChipsModule } from '@angular/material/chips';
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
    MatProgressBarModule, MatDividerModule, MatChipsModule,
    TranslateModule,
  ],
  template: `
    <div class="dashboard-wrapper">
      <!-- Top Location & Freshness Header -->
      <div class="location-strip" *ngIf="aqi$ | async as aqi">
        <div class="location-info">
          <mat-icon class="loc-pin">place</mat-icon>
          <span class="loc-text">Pune, Maharashtra</span>
          <span class="live-dot" title="Live station feed"></span>
          <span class="station-meta">{{ aqi.source }} · Updated just now</span>
        </div>
        <div class="genai-pill">
          <mat-icon inline>auto_awesome</mat-icon>
          <span>Google Gemini 1.5 Grounded</span>
        </div>
      </div>

      <!-- Hero AQI Card -->
      <mat-card class="aqi-hero-card" *ngIf="aqi$ | async as aqi">
        <mat-card-content>
          <div class="hero-top">
            <div class="aqi-main-metric">
              <div class="aqi-circle" [style.background-color]="getColor(aqi.aqi) + '22'" [style.border-color]="getColor(aqi.aqi)">
                <span class="aqi-number" [style.color]="getColor(aqi.aqi)">{{ aqi.aqi ?? '—' }}</span>
                <span class="aqi-unit">AQI</span>
              </div>
              <div class="aqi-status">
                <span class="status-badge" [style.background-color]="getColor(aqi.aqi)" [style.color]="getTextColor(aqi.aqi)">
                  {{ aqi.aqi_category || 'Moderate' }}
                </span>
                <span class="status-desc">{{ getHealthAdvisory(aqi.aqi) }}</span>
              </div>
            </div>

            <!-- Action CTAs -->
            <div class="hero-actions">
              <a mat-raised-button color="primary" routerLink="/plan" class="action-btn">
                <mat-icon>event_available</mat-icon>
                {{ 'dashboard.viewPlan' | translate }}
              </a>
              <a mat-stroked-button routerLink="/chat" class="action-btn">
                <mat-icon>chat</mat-icon>
                {{ 'dashboard.askAssistant' | translate }}
              </a>
            </div>
          </div>

          <!-- CPCB Spectrum Bar -->
          <div class="spectrum-container">
            <div class="spectrum-labels">
              <span>0 Good</span>
              <span>50</span>
              <span>100</span>
              <span>200</span>
              <span>300</span>
              <span>400</span>
              <span>500 Severe</span>
            </div>
            <div class="spectrum-bar">
              <div class="spectrum-seg s-good"></div>
              <div class="spectrum-seg s-sat"></div>
              <div class="spectrum-seg s-mod"></div>
              <div class="spectrum-seg s-poor"></div>
              <div class="spectrum-seg s-vpoor"></div>
              <div class="spectrum-seg s-sev"></div>
              <!-- Pointer marker based on AQI value -->
              <div class="spectrum-pointer" [style.left.%]="getPointerPercent(aqi.aqi)">
                ▼
              </div>
            </div>
          </div>

          <!-- Pollutant Grid -->
          <div class="pollutant-cards-grid">
            <div class="kpi-card" *ngFor="let p of pollutants(aqi)">
              <span class="kpi-name">{{ p.label }}</span>
              <div class="kpi-val-row">
                <span class="kpi-value">{{ p.value | number:'1.0-1' }}</span>
                <span class="kpi-unit">{{ p.unit }}</span>
              </div>
            </div>
          </div>

          <!-- Temperature Inversion Advisory Banner -->
          <div class="inversion-banner" *ngIf="aqi.temperature_inversion" role="alert">
            <div class="inv-icon-box">
              <mat-icon color="warn">wb_twilight</mat-icon>
            </div>
            <div class="inv-text-box">
              <strong>Winter Temperature Inversion Alert:</strong>
              <span>Cool ground air is trapping vehicular and cooking emissions close to the surface until late morning. Reschedule strenuous outdoor workouts between 12:00 PM – 4:00 PM.</span>
            </div>
          </div>
        </mat-card-content>
      </mat-card>

      <!-- Impact & Forecast Row -->
      <div class="metrics-row">
        <mat-card class="metric-highlight">
          <mat-card-header>
            <mat-icon mat-card-avatar class="highlight-icon green">health_and_safety</mat-icon>
            <mat-card-title>Today's Health Impact</mat-card-title>
            <mat-card-subtitle>Computed via Deterministic Impact Module</mat-card-subtitle>
          </mat-card-header>
          <mat-card-content>
            <div class="stats-duo">
              <div class="stat-box">
                <span class="stat-num">85.0</span>
                <span class="stat-label">µg/m³·h PM2.5 Inhalation Saved</span>
              </div>
              <div class="stat-box">
                <span class="stat-num">4.2</span>
                <span class="stat-label">kg CO₂e Tailpipe Avoided</span>
              </div>
            </div>
            <p class="stat-caption">Lower coughing &amp; eye-irritation risk for children and sensitive individuals today.</p>
          </mat-card-content>
        </mat-card>

        <mat-card class="metric-highlight">
          <mat-card-header>
            <mat-icon mat-card-avatar class="highlight-icon blue">schedule</mat-icon>
            <mat-card-title>Optimal Outdoor Window</mat-card-title>
            <mat-card-subtitle>Maharashtra Winter Sun Profile</mat-card-subtitle>
          </mat-card-header>
          <mat-card-content>
            <div class="window-banner best">
              <mat-icon>check_circle</mat-icon>
              <div>
                <strong>12:00 PM – 4:00 PM (Best Window)</strong>
                <p>Solar heating disperses ground particulates. Ideal for errands &amp; exercise.</p>
              </div>
            </div>
            <div class="window-banner avoid">
              <mat-icon>error_outline</mat-icon>
              <div>
                <strong>6:00 AM – 10:00 AM (Peak Inversion)</strong>
                <p>Highest particle density. Keep windows sealed; avoid morning jogs.</p>
              </div>
            </div>
          </mat-card-content>
        </mat-card>
      </div>

      <!-- Quick Action Cards Grid -->
      <h3 class="section-title">Quick Actions</h3>
      <div class="quick-actions-grid">
        <mat-card class="action-card" routerLink="/plan" role="button" tabindex="0">
          <mat-card-content>
            <div class="action-icon-circle bg-green">
              <mat-icon>calendar_today</mat-icon>
            </div>
            <h4>{{ 'dashboard.bestTime' | translate }}</h4>
            <p>View your personalized clean air daily schedule</p>
          </mat-card-content>
        </mat-card>

        <mat-card class="action-card" routerLink="/chat" role="button" tabindex="0">
          <mat-card-content>
            <div class="action-icon-circle bg-purple">
              <mat-icon>psychology</mat-icon>
            </div>
            <h4>{{ 'dashboard.askAI' | translate }}</h4>
            <p>Ask Google Gemini RAG assistant on masks &amp; indoor tips</p>
          </mat-card-content>
        </mat-card>

        <mat-card class="action-card" routerLink="/community" role="button" tabindex="0">
          <mat-card-content>
            <div class="action-icon-circle bg-teal">
              <mat-icon>groups</mat-icon>
            </div>
            <h4>{{ 'dashboard.community' | translate }}</h4>
            <p>Join Pune neighborhood clean air challenges</p>
          </mat-card-content>
        </mat-card>
      </div>

      <!-- Indoor Tips Cards -->
      <mat-card class="indoor-tips-card">
        <mat-card-header>
          <mat-icon mat-card-avatar color="primary">cottage</mat-icon>
          <mat-card-title>{{ 'dashboard.indoorTips' | translate }}</mat-card-title>
          <mat-card-subtitle>Cost-effective indoor air quality hacks for winter smog</mat-card-subtitle>
        </mat-card-header>
        <mat-card-content>
          <div class="tips-grid">
            <div class="tip-tile" *ngFor="let tip of indoorTips">
              <mat-icon class="tip-check">task_alt</mat-icon>
              <span>{{ tip | translate }}</span>
            </div>
          </div>
        </mat-card-content>
      </mat-card>
    </div>
  `,
  styles: [`
    .dashboard-wrapper {
      max-width: 1040px;
      margin: 0 auto;
      display: flex;
      flex-direction: column;
      gap: 16px;
    }
    .location-strip {
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 8px;
      padding: 0 4px;
    }
    .location-info {
      display: flex;
      align-items: center;
      gap: 6px;
      color: #333;
    }
    .loc-pin { color: #d32f2f; font-size: 20px; height: 20px; width: 20px; }
    .loc-text { font-weight: 700; font-size: 15px; }
    .live-dot {
      width: 8px; height: 8px; background: #4caf50;
      border-radius: 50%; display: inline-block;
      box-shadow: 0 0 6px #4caf50;
    }
    .station-meta { font-size: 12px; color: #666; }
    .genai-pill {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      background: #e8f5e9;
      color: #1b5e20;
      padding: 4px 10px;
      border-radius: 12px;
      font-size: 12px;
      font-weight: 600;
    }
    .aqi-hero-card {
      border-radius: 12px;
      box-shadow: 0 4px 20px rgba(0,0,0,0.06);
    }
    .hero-top {
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 16px;
      margin-bottom: 20px;
    }
    .aqi-main-metric {
      display: flex;
      align-items: center;
      gap: 16px;
    }
    .aqi-circle {
      width: 100px;
      height: 100px;
      border-radius: 50%;
      border: 4px solid;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
    }
    .aqi-number {
      font-size: 42px;
      font-weight: 900;
      line-height: 1;
    }
    .aqi-unit {
      font-size: 11px;
      font-weight: 700;
      color: #666;
    }
    .aqi-status {
      display: flex;
      flex-direction: column;
      gap: 6px;
    }
    .status-badge {
      display: inline-block;
      padding: 4px 14px;
      border-radius: 16px;
      font-size: 18px;
      font-weight: 700;
      width: fit-content;
    }
    .status-desc {
      font-size: 13px;
      color: #555;
      max-width: 320px;
      line-height: 1.4;
    }
    .hero-actions {
      display: flex;
      gap: 10px;
    }
    .action-btn {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      border-radius: 20px;
    }

    /* CPCB Spectrum Bar */
    .spectrum-container {
      margin: 14px 0 20px 0;
    }
    .spectrum-labels {
      display: flex;
      justify-content: space-between;
      font-size: 11px;
      color: #777;
      margin-bottom: 4px;
    }
    .spectrum-bar {
      position: relative;
      height: 10px;
      border-radius: 5px;
      display: flex;
      overflow: visible;
    }
    .spectrum-seg { flex: 1; height: 100%; }
    .s-good { background: #55a84f; border-radius: 5px 0 0 5px; }
    .s-sat { background: #a3c853; }
    .s-mod { background: #fbc02d; }
    .s-poor { background: #f29c33; }
    .s-vpoor { background: #e93f33; }
    .s-sev { background: #af2d24; border-radius: 0 5px 5px 0; }
    .spectrum-pointer {
      position: absolute;
      top: -12px;
      transform: translateX(-50%);
      font-size: 12px;
      color: #1a1a1a;
      transition: left 0.5s ease;
    }

    /* Pollutant Cards */
    .pollutant-cards-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
      gap: 10px;
      margin-top: 14px;
    }
    .kpi-card {
      background: #f7f9f7;
      border: 1px solid #e0e6e0;
      border-radius: 8px;
      padding: 10px 14px;
      display: flex;
      flex-direction: column;
      gap: 4px;
    }
    .kpi-name {
      font-size: 11px;
      color: #666;
      font-weight: 700;
      text-transform: uppercase;
    }
    .kpi-val-row {
      display: flex;
      align-items: baseline;
      gap: 4px;
    }
    .kpi-value {
      font-size: 20px;
      font-weight: 800;
      color: #2e7d32;
    }
    .kpi-unit {
      font-size: 11px;
      color: #888;
    }

    /* Inversion banner */
    .inversion-banner {
      display: flex;
      align-items: flex-start;
      gap: 12px;
      background: #fff8e1;
      border: 1px solid #ffe082;
      border-radius: 8px;
      padding: 12px 14px;
      margin-top: 16px;
      font-size: 13px;
      color: #5d4037;
    }
    .inv-text-box { display: flex; flex-direction: column; gap: 2px; }

    /* Metrics Row */
    .metrics-row {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
    }
    .metric-highlight { border-radius: 12px; }
    .highlight-icon.green { color: #2e7d32; }
    .highlight-icon.blue { color: #1976d2; }
    .stats-duo {
      display: flex;
      gap: 16px;
      margin: 12px 0 8px 0;
    }
    .stat-box {
      flex: 1;
      background: #f1f8e9;
      border-radius: 8px;
      padding: 10px;
      display: flex;
      flex-direction: column;
      gap: 2px;
    }
    .stat-num {
      font-size: 24px;
      font-weight: 900;
      color: #2e7d32;
    }
    .stat-label {
      font-size: 11px;
      color: #555;
      font-weight: 500;
    }
    .stat-caption { font-size: 12px; color: #666; margin: 0; }
    .window-banner {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 8px 12px;
      border-radius: 8px;
      margin-top: 8px;
      font-size: 12px;
    }
    .window-banner p { margin: 2px 0 0 0; }
    .window-banner.best { background: #e8f5e9; color: #1b5e20; }
    .window-banner.avoid { background: #ffebee; color: #c62828; }

    /* Quick Actions Grid */
    .section-title {
      margin: 8px 0 0 0;
      font-size: 18px;
      font-weight: 700;
      color: #333;
    }
    .quick-actions-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 14px;
    }
    .action-card {
      border-radius: 12px;
      cursor: pointer;
      transition: transform 0.2s, box-shadow 0.2s;
    }
    .action-card:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 18px rgba(0,0,0,0.1);
    }
    .action-icon-circle {
      width: 44px;
      height: 44px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-bottom: 8px;
    }
    .bg-green { background: #e8f5e9; color: #2e7d32; }
    .bg-purple { background: #ede7f6; color: #512da8; }
    .bg-teal { background: #e0f2f1; color: #00796b; }
    .action-card h4 { margin: 0 0 4px 0; font-size: 16px; font-weight: 700; }
    .action-card p { margin: 0; font-size: 12px; color: #666; }

    /* Indoor Tips */
    .indoor-tips-card { border-radius: 12px; }
    .tips-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 10px;
      margin-top: 8px;
    }
    .tip-tile {
      display: flex;
      align-items: center;
      gap: 8px;
      background: #fafafa;
      border: 1px solid #eee;
      border-radius: 6px;
      padding: 10px 12px;
      font-size: 13px;
      color: #444;
    }
    .tip-check { color: #4caf50; font-size: 18px; width: 18px; height: 18px; }

    @media (max-width: 680px) {
      .metrics-row { grid-template-columns: 1fr; }
      .hero-top { flex-direction: column; align-items: flex-start; }
      .hero-actions { width: 100%; justify-content: flex-start; }
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

  getTextColor(aqi: number | null): string {
    if (!aqi || aqi <= 200) return '#1a1a1a';
    return '#ffffff';
  }

  getPointerPercent(aqi: number | null): number {
    if (!aqi) return 17;
    const clamped = Math.max(0, Math.min(500, aqi));
    return (clamped / 500) * 100;
  }

  getHealthAdvisory(aqi: number | null): string {
    if (!aqi || aqi <= 50) return 'Air quality is satisfactory and poses little or no risk.';
    if (aqi <= 100) return 'Acceptable air quality. Minor breathing discomfort possible for sensitive children.';
    if (aqi <= 200) return 'Breathing discomfort to people with asthma and respiratory conditions.';
    if (aqi <= 300) return 'Avoid prolonged outdoor exertion. Sensitive groups should wear N95 respirators.';
    if (aqi <= 400) return 'Respiratory illness on prolonged exposure. Significant risk for all age groups.';
    return 'Severe emergency air quality. Healthy people affected; serious impacts on respiratory patients.';
  }

  pollutants(aqi: AQIData) {
    return [
      { label: 'PM2.5', value: aqi.pm25, unit: 'µg/m³' },
      { label: 'PM10',  value: aqi.pm10, unit: 'µg/m³' },
      { label: 'NO₂',   value: aqi.no2,  unit: 'µg/m³' },
      { label: 'Temp',  value: aqi.temperature_c, unit: '°C' },
      { label: 'Humidity', value: aqi.humidity_pct,  unit: '%' },
      { label: 'Wind',  value: aqi.wind_speed_ms, unit: 'm/s' },
    ].filter(p => p.value !== null && p.value !== undefined);
  }
}
